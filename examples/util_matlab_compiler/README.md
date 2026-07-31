# Packaging Zaber Motion Library with MATLAB Compiler

*By Colby Sparks*

This example demonstrates how to use MATLAB Compiler to build and run two kinds of MATLAB applications which use the
Zaber Motion Library toolbox: a standalone console application (`src/main.m`) and a Windows desktop application with
a simple UI for controlling a Zaber device (`src/desktop_app.m`).

## MATLAB Compiler

MATLAB Compiler is a tool which allows users to package MATLAB code into standalone applications.
During the build process, it will perform a dependency analysis of a project to determine exactly which files
need to be included in the final packaged application, but binary dependencies such as `*.mex` files
and shared libraries (`*.dll`/`*.so`/`*.dylib`) will not be included automatically.

The Zaber Motion Library toolbox includes some binary dependencies, namely a shared library and
its corresponding thunk file, so the paths to these binary files must be specified manually.

## Prerequisites

The user must have the [MATLAB Compiler](https://www.mathworks.com/products/compiler.html) and [Zaber Motion Library toolbox](https://software.zaber.com/motion-library/docs/tutorials/install/matlab) (version `>=8.4.0`) installed.
Additionally, in order to run the `matlab -batch` command below, MATLAB must be added to the system [PATH](https://stackoverflow.com/questions/4822400/register-an-exe-so-you-can-run-it-from-any-command-line-in-windows).

This code example has been tested with MATLAB R2026a.

## Standalone Application

There are several different ways of configuring MATLAB Compiler to build a standalone application.
In this example we use the [compiler.build.standaloneApplication](https://www.mathworks.com/help/compiler/compiler.build.standaloneapplication.html) function with [StandaloneApplicationOptions](https://www.mathworks.com/help/compiler/compiler.build.standaloneapplicationoptions.html) object.
It is also possible to configure and build an application using the [Standalone Application Compiler](https://www.mathworks.com/help/compiler/create-application-using-standalone-application-compiler-app.html) in the MATLAB IDE.

The [build_standalone_app.m](./build_standalone_app.m) script contains all the logic for packaging the Zaber Motion Library toolbox
with the program contained in [src/main.m](./src/main.m). The most important thing to note is the following line where we assign
the return value from `zaber.motion.Helper.getCompilerDependencies` to the `AdditionalFiles` field of the build options object:

```matlab
buildOpts.AdditionalFiles = zaber.motion.Helper.getCompilerDependencies();
```

**Note**: If you are using the Standalone Application Compiler in the MATLAB IDE, the files whose paths are returned from
`zaber.motion.Helper.getCompilerDependencies` need to be added manually under "Files Required for Standalone to Run".

### Building the Application

To build the standalone application, clone this repository with `git` (or download the project), then either:
- Open the `util_matlab_compiler` directory in your MATLAB IDE and run `build_standalone_app`.
- In the command line, navigate to the `util_matlab_compiler` directory and run `matlab -batch build_standalone_app`.

The script places the packaged application in the `ZaberStandaloneApp/output/build` folder.

### Running the Application

#### Windows

To run the application in Windows, you can either locate the `ZaberStandaloneApp.exe` file directly in File Explorer or use the following command in PowerShell:

```shell
cd examples/util_matlab_compiler
.\ZaberStandaloneApp\output\build\ZaberStandaloneApp.exe
```

#### Linux / macOS

On Linux/macOS, MATLAB Compiler generates a shell script `run_ZaberStandaloneApp.sh` which requires the path to your MATLAB Runtime (or MATLAB installation) as the first argument:

```bash
cd examples/util_matlab_compiler
./ZaberStandaloneApp/output/build/run_ZaberStandaloneApp.sh <deployedMcrRoot>
```

Where `<deployedMcrRoot>` is the path to your MATLAB install.

## Windows Desktop Application

MATLAB Compiler can also package a program as a Windows desktop application using the
[compiler.build.standaloneWindowsApplication](https://www.mathworks.com/help/compiler/compiler.build.standalonewindowsapplication.html) function.
Unlike a standalone application, a desktop application does not open a console window when launched,
which makes it a better fit for GUI programs. Note that this build function is only supported on Windows.

The application source in [src/desktop_app.m](./src/desktop_app.m) implements a simple UI which allows the user to
connect to a Zaber device and:

- Home the device
- Move toward or away from the home position at a chosen velocity
- Move to an absolute position in mm

The serial port can be entered into the input box after startup. Optionally, you can edit the following constants
at the top of `desktop_app.m`:

- `DEVICE_ADDRESS`: The device address of the device you'd like to connect to
- `AXIS_NUMBER`: The axis number of the axis you'd like to control on the device (`1` for most integrated devices)

The [build_windows_desktop_app.m](./build_windows_desktop_app.m) script configures the build the same way as the
standalone application, including assigning `zaber.motion.Helper.getCompilerDependencies()` to `AdditionalFiles`.
It also sets the `ExecutableSplashScreen` option so that a splash image is displayed while the MATLAB Runtime loads,
which can take several seconds.

### Building the Application

To build the desktop application, either:

- Open the `util_matlab_compiler` directory in your MATLAB IDE and run `build_windows_desktop_app`.
- In the command line, navigate to the `util_matlab_compiler` directory and run `matlab -batch build_windows_desktop_app`.

The script places the packaged application in the `ZaberDesktopApp/output/build` folder.

You can also run the app directly in MATLAB (on any platform) by navigating to the `src` directory and running `desktop_app`.

### Running the Application

To run the application, you can either locate the `ZaberDesktopApp.exe` file directly in File Explorer or use the following command in PowerShell:

```shell
cd examples/util_matlab_compiler
.\ZaberDesktopApp\output\build\ZaberDesktopApp.exe
```
