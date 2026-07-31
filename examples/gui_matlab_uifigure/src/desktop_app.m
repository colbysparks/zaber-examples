function desktop_app()
    % Simple UI for connecting to a Zaber device and moving one of its axes.
    import zaber.motion.Units;
    import zaber.motion.ascii.Connection;

    DEVICE_ADDRESS = 1;
    AXIS_NUMBER = 1;
    POSITION_POLL_PERIOD = 0.1; % seconds

    connection = [];
    stageAxis = [];

    fig = uifigure(Name="Zaber Desktop App");
    fig.Position(3:4) = [480 480];
    fig.CloseRequestFcn = @(~, ~) onClose();

    layout = uigridlayout(fig, [5 1], RowHeight={'fit', 'fit', 'fit', 'fit', 'fit'});

    % Device info
    infoPanel = uipanel(layout, Title="Device");
    infoLayout = uigridlayout(infoPanel, [5 2], ColumnWidth={'fit', '1x'}, RowSpacing=2);
    statusValue = addInfoRow(infoLayout, "Status:", "Not Connected");
    nameValue = addInfoRow(infoLayout, "Name:", "");
    deviceIdValue = addInfoRow(infoLayout, "Device ID:", "");
    serialValue = addInfoRow(infoLayout, "Serial #:", "");
    firmwareValue = addInfoRow(infoLayout, "Firmware Version:", "");

    % Connection controls
    connectLayout = uigridlayout(layout, [1 2], ColumnWidth={'1x', 'fit'}, Padding=0);
    portField = uieditfield(connectLayout, "text", Placeholder="Enter serial port...");
    connectButton = uibutton(connectLayout, Text="Connect", ButtonPushedFcn=@(~, ~) onConnect());

    % Motion controls
    motionPanel = uipanel(layout, Title="Motion");
    motionLayout = uigridlayout(motionPanel, [3 3], ColumnWidth={'1x', '1x', '1x'});
    homeButton = uibutton(motionLayout, Text="Home", ButtonPushedFcn=@(~, ~) onHome());
    stopButton = uibutton(motionLayout, Text="Stop", ButtonPushedFcn=@(~, ~) onStop());
    stopButton.Layout.Column = [2 3];
    velocityField = uieditfield(motionLayout, "numeric", Value=5, Limits=[0 Inf], ...
        ValueDisplayFormat="%.1f mm/s", Tooltip="Velocity");
    towardHomeButton = uibutton(motionLayout, Text="Move Toward Home", ...
        ButtonPushedFcn=@(~, ~) onMoveVelocity(-1));
    awayFromHomeButton = uibutton(motionLayout, Text="Move Away From Home", ...
        ButtonPushedFcn=@(~, ~) onMoveVelocity(1));
    absPositionField = uieditfield(motionLayout, "numeric", Value=0, Limits=[0 Inf], ...
        ValueDisplayFormat="%.3f mm", Tooltip="Target position");
    moveAbsoluteButton = uibutton(motionLayout, Text="Move To Position", ...
        ButtonPushedFcn=@(~, ~) onMoveAbsolute());
    moveAbsoluteButton.Layout.Column = [2 3];

    motionControls = [homeButton stopButton velocityField towardHomeButton ...
        awayFromHomeButton absPositionField moveAbsoluteButton];
    set(motionControls, Enable="off");

    % Position readout
    positionLayout = uigridlayout(layout, [1 2], ColumnWidth={'fit', '1x'}, Padding=0);
    uilabel(positionLayout, Text="Position:", FontWeight="bold");
    positionValue = uilabel(positionLayout, Text="?");

    errorLabel = uilabel(layout, Text="", FontColor=[0.8 0 0], WordWrap="on");

    positionTimer = timer(Period=POSITION_POLL_PERIOD, ExecutionMode="fixedSpacing", ...
        TimerFcn=@(~, ~) updatePosition());

    function valueLabel = addInfoRow(parent, labelText, valueText)
        uilabel(parent, Text=labelText, FontWeight="bold");
        valueLabel = uilabel(parent, Text=valueText);
    end

    function onConnect()
        try
            connection = Connection.openSerialPort(portField.Value);
            connection.enableAlerts();
            device = connection.getDevice(DEVICE_ADDRESS);
            device.identify();
            stageAxis = device.getAxis(AXIS_NUMBER);

            statusValue.Text = "Connected";
            nameValue.Text = device.Name;
            deviceIdValue.Text = string(device.DeviceId);
            serialValue.Text = string(device.SerialNumber);
            firmwareVersion = device.FirmwareVersion;
            firmwareValue.Text = sprintf("%d.%d", firmwareVersion.Major, firmwareVersion.Minor);

            portField.Enable = "off";
            connectButton.Enable = "off";
            set(motionControls, Enable="on");
            start(positionTimer);
            errorLabel.Text = "";
        catch err
            if ~isempty(connection)
                connection.close();
                connection = [];
            end
            errorLabel.Text = err.message;
        end
    end

    function onHome()
        runCommand(@() stageAxis.home(waitUntilIdle=false));
    end

    function onStop()
        runCommand(@() stageAxis.stop(waitUntilIdle=false));
    end

    function onMoveVelocity(direction)
        velocity = direction * velocityField.Value;
        runCommand(@() stageAxis.moveVelocity(velocity, Units.VelocityMillimetresPerSecond));
    end

    function onMoveAbsolute()
        runCommand(@() stageAxis.moveAbsolute(absPositionField.Value, ...
            Units.LengthMillimetres, waitUntilIdle=false));
    end

    function runCommand(command)
        try
            command();
            errorLabel.Text = "";
        catch err
            errorLabel.Text = err.message;
        end
    end

    function updatePosition()
        try
            position = stageAxis.getPosition(Units.LengthMillimetres);
            positionValue.Text = sprintf("%.3f mm", position);
        catch err
            positionValue.Text = "?";
            errorLabel.Text = err.message;
        end
    end

    function onClose()
        stop(positionTimer);
        delete(positionTimer);
        try
            if ~isempty(connection)
                connection.close();
            end
        catch
            % Ignore errors so the window always closes.
        end
        delete(fig);
    end
end
