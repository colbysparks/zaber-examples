assert(ispc, "compiler.build.standaloneWindowsApplication is only supported on Windows.");

projectRoot = fileparts(mfilename('fullpath'));

% Create target build options object, set build properties and build.
buildOpts = compiler.build.StandaloneApplicationOptions(fullfile(projectRoot, "src", "desktop_app.m"));
buildOpts.AdditionalFiles = [zaber.motion.Helper.getCompilerDependencies(), ...
    fullfile(projectRoot, "img", "zaber_logo.png"), ...
    fullfile(projectRoot, "img", "app_icon.png")];
buildOpts.OutputDir = fullfile(projectRoot, "ZaberDesktopApp", "output", "build");
buildOpts.Verbose = true;
buildOpts.ExecutableName = "ZaberDesktopApp";
buildOpts.ExecutableVersion = "1.0.0";
buildOpts.ExecutableIcon = fullfile(projectRoot, "img", "app_icon.png");
buildOpts.ExecutableSplashScreen = fullfile(projectRoot, "img", "splash_screen.png");

compiler.build.standaloneWindowsApplication(buildOpts);
