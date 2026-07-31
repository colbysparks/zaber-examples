# MATLAB GUI for Controlling a Zaber Device

*By Colby Sparks*

This example implements a simple MATLAB desktop app for controlling a single axis of a Zaber device.
The UI is built programmatically with [uifigure](https://www.mathworks.com/help/matlab/ref/uifigure.html)
and UI component functions, and lets the user:

- Connect to a device over a serial port
- View basic device information and a live position readout
- Home the axis or stop it at any time
- Move toward or away from the home position at a chosen velocity
- Move to an absolute position in mm

The example also includes a build script for packaging the app as a Windows desktop application
with MATLAB Compiler.

## Hardware Requirements

Any Zaber device with a linear axis, connected to the computer by serial port or USB.

## Dependencies

The app requires the [Zaber Motion Library toolbox](https://software.zaber.com/motion-library/docs/tutorials/install/matlab) (version `>=8.4.0`).
Building the Windows desktop application additionally requires the [MATLAB Compiler](https://www.mathworks.com/products/compiler.html).

This code example has been tested with MATLAB R2026a.

## Configuration

The serial port can be entered into the input box after startup. Optionally, you can edit the following constants
at the top of [src/desktop_app.m](./src/desktop_app.m):

- `DEVICE_ADDRESS`: The device address of the device you'd like to connect to
- `AXIS_NUMBER`: The axis number of the axis you'd like to control on the device (`1` for most integrated devices)

## Running the App

In MATLAB, navigate to this example's `src` directory and run `desktop_app`. The app runs on any platform.

All of the UI callbacks are nested functions sharing the connection state of the parent function.
Motion commands are sent with `waitUntilIdle` set to `false` so the UI stays responsive while the axis moves,
and a timer polls the axis position to keep the readout current. Any command error is displayed at the
bottom of the window.

## Building a Windows Desktop Application

MATLAB Compiler can package a program as a Windows desktop application using the
[compiler.build.standaloneWindowsApplication](https://www.mathworks.com/help/compiler/compiler.build.standalonewindowsapplication.html) function.
Unlike a standalone console application, a desktop application does not open a console window when launched,
which makes it a better fit for GUI programs. Note that this build function is only supported on Windows.

The [build_windows_desktop_app.m](./build_windows_desktop_app.m) script configures the build, most importantly
assigning `zaber.motion.Helper.getCompilerDependencies()` to the `AdditionalFiles` option so that the
Zaber Motion Library's binary dependencies are packaged with the app. This is explained in more detail in the
[Packaging Zaber Motion Library with MATLAB Compiler](../util_matlab_compiler/README.md) example.
The script also sets the `ExecutableSplashScreen` option so that a splash image is displayed while the
MATLAB Runtime loads, which can take several seconds.

**Note**: The build entry point can also be an App Designer file (`*.mlapp`) instead of a `*.m` script.

To build the desktop application, either:

- Open the `gui_matlab_uifigure` directory in your MATLAB IDE and run `build_windows_desktop_app`.
- In the command line, navigate to the `gui_matlab_uifigure` directory and run `matlab -batch build_windows_desktop_app`.

The script places the packaged application in the `ZaberDesktopApp/output/build` folder.

To run the application, you can either locate the `ZaberDesktopApp.exe` file directly in File Explorer or use the following command in PowerShell:

```shell
cd examples/gui_matlab_uifigure
.\ZaberDesktopApp\output\build\ZaberDesktopApp.exe
```
