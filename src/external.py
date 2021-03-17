######################################################################
#                              EXTERNAL                              #
######################################################################

import utils
from Classes.PathManager import PathManager
from urllib.request import urlretrieve
from Classes.Metadata import Metadata
from subprocess import PIPE, Popen
from extension import *
from halo import Halo
from colorama import Fore
import json as js
import mslex
import sys
import os


def handle_python_package(package_name: str, version: str, mode: str, metadata: Metadata):
    """
    Installs a python package handling metadata for the method

    #### Arguments
        package_name (str): The name of the python package to be installed
        version (str): The version of the python package to be installed
        mode (str): The method (installation/uninstallation)
        metadata (`Metadata`): Metadata for the method
    """    
    command = ''

    valid = Popen(mslex.split('pip --version'), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    _, err = valid.communicate()

    if err:
        click.echo(click.style('Python Is Not Installed. Exit Code [0011]', fg='red'))
        utils.disp_error_msg(utils.get_error_message('0011', 'install', package_name, None), metadata)
        utils.handle_exit('ERROR', None, metadata)
    
    if mode == 'install':
        command = 'python -m pip install --upgrade --no-input'

        command += f' {package_name}'
        if version != 'latest':
            command += f'=={version}'

        proc = Popen(mslex.split(command), stdin=PIPE,
                        stdout=PIPE, stderr=PIPE)

        py_version = sys.version.split()
        for line in proc.stdout:
            line = line.decode('utf-8')

            if f'Collecting {package_name}' in line:
                write(f'Python v{py_version[0]} :: Collecting {package_name}', 'green', metadata)
            if 'Downloading' in line and package_name in line:
                write(
                    f'Python v{py_version[0]} :: Downloading {package_name}', 'green', metadata)

            if 'Installing collected packages' in line and package_name in line:
                write(
                    f'Python v{py_version[0]} :: Installing {package_name}', 'green', metadata)

            if f'Requirement ' in line and package_name in line:
                write(
                    f'Python v{py_version[0]} :: {package_name} Is Already Installed And On The Latest Version ==> {line.split()[-1]}', 'yellow', metadata)
                break

            if 'Successfully installed' in line and package_name in line:
                ver = line.split('-')[1]
                write(
                    f'Python v{py_version[0]} :: Successfully Installed {package_name} {ver}', 'green', metadata)

            if 'You should consider upgrading via' in line:
                wants = utils.confirm(
                    'Would you like to upgrade your pip version?')
                if wants:
                    write('Updating Pip Version', 'green', metadata)
                    Popen(mslex.split('python -m pip install --upgrade pip'))

    elif mode == 'uninstall':
        command = 'python -m pip uninstall --no-input --yes'

        command += f' {package_name}'

        proc = Popen(mslex.split(command), stdin=PIPE,
                        stdout=PIPE, stderr=PIPE)

        py_version = sys.version.split()

        for line in proc.stdout:
            line = line.decode('utf-8')
            if 'Uninstalling' in line and package_name in line:
                write(
                    f'Python v{py_version[0]} :: Uninstalling {package_name}', 'green', metadata)

            if 'Successfully uninstalled' in line and package_name in line:
                ver = line.split('-')[1]
                write(
                    f'Python v{py_version[0]} :: Successfully Uninstalled {package_name} {ver}', 'green', metadata)

        _, err = proc.communicate()

        if err:
            err = err.decode('utf-8')
            if f'WARNING: Skipping {package_name}' in err:
                write(
                    f'Python v{py_version[0]} :: Could Not Find Any Installations Of {package_name}', 'yellow', metadata)


def handle_node_package(package_name: str, mode: str, metadata: Metadata):
    """
    Installs a node/npm package handling metadata for the method

    #### Arguments
        package_name (str): The name of the node/npm package to be installed
        version (str): The version of the node/npm package to be installed
        mode (str): The method (installation/uninstallation)
        metadata (`Metadata`): Metadata for the method
    """    
    version_proc = Popen(mslex.split('npm --version'), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    version, err = version_proc.communicate()
    version = version.decode().strip()

    if err:
        click.echo(click.style('npm Or node Is Not Installed. Exit Code [0011]', fg='bright_yellow'))
        utils.disp_error_msg(utils.get_error_message('0011', 'install', package_name, None), metadata)
        utils.handle_exit('ERROR', None, metadata)


    if mode == 'install':
        proc = Popen(mslex.split(f'npm i {package_name} -g'), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        write(f'npm v{version} :: Collecting {package_name}', 'green', metadata)
        package_version = None
        for line in proc.stdout:
            line = line.decode()

            if 'node install.js' in line:
                write(f'npm v{version} :: Running `node install.js` for {package_name}', 'green', metadata)
            if package_name in line and '@' in line and 'install' in line or ' postinstall' in line:
                package_version = line.split()[1]
                write(f'npm v{version} :: {package_version} Installing To <=> "{line.split()[3]}"', 'green', metadata)

            if 'Success' in line and package_name in line or 'added' in line:
                write(f'npm v{version} :: Successfully Installed {package_version}', 'green', metadata)
            if 'updated' in line:
                if package_version:
                    write(f'npm v{version} :: Sucessfully Updated {package_version}', 'green', metadata)
                else:
                    write(f'npm v{version} :: Sucessfully Updated {package_name}', 'green', metadata)


    else:
        proc = Popen(mslex.split(f'npm uninstall -g {package_name}'), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        for line in proc.stdout:
            line = line.decode()
            if 'up to date' in line:
                write(f'npm v{version} :: Could Not Find Any Existing Installations Of {package_name}', 'yellow', metadata)
            if 'removed' in line:
                number = line.split(' ')[1].strip()
                time = line.split(' ')[4].strip()
                write(f'npm v{version} :: Sucessfully Uninstalled {package_name} And {number} Other Dependencies in {time}', 'green', metadata)


def handle_vscode_extension(package_name: str, mode: str, metadata: Metadata):
    """
    Installs a visual studio code package handling metadata for the method

    #### Arguments
        package_name (str): The name of the visual studio code package to be installed
        version (str): The version of the visual studio code package to be installed
        mode (str): The method (installation/uninstallation)
        metadata (`Metadata`): Metadata for the method
    """
    base_c = 'code'
    
    output = Popen(mslex.split('code --version'), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    version, _ = output.communicate()
    version = version.decode()         
    if output.returncode != 0:
        output = Popen(mslex.split('code-insiders --version'), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        version, _ = output.communicate()
        version = version.decode()
        base_c = 'code-insiders'
        if output.returncode != 0:
            click.echo(click.style('Visual Studio Code Or vscode Is Not Installed. Exit Code [0111]', fg='bright_yellow'))
            utils.disp_error_msg(utils.get_error_message('0111', 'install', package_name, None), metadata)
            utils.handle_exit('error', metadata)

    version = version.strip().split('\n')[0]
    
    if mode == 'install':
        command = f'{base_c} --install-extension {package_name} --force'
        proc = Popen(mslex.split(command), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        for line in proc.stdout:
            line = line.decode()

            if 'Installing extensions' in line:
                if not metadata.no_color:
                    write(f'Code v{version} :: Installing {Fore.MAGENTA}{package_name}{Fore.RESET}', 'green', metadata)
                else:
                    write(f'Code v{version} :: Installing {package_name}', 'white', metadata)

            if 'is already installed' in line:
                if not metadata.no_color:
                    write(f'{Fore.GREEN}Code v{version} :: {Fore.MAGENTA}{package_name}{Fore.YELLOW} Is Already Installed!', 'white', metadata)
                else:
                    write(f'Code v{version} :: {package_name} Is Already Installed!', 'white', metadata)

            if 'was successfully installed' in line:
                if not metadata.no_color:
                    write(f'{Fore.GREEN}Code v{version} :: Successfully Installed {Fore.MAGENTA}{package_name}{Fore.RESET}', 'green', metadata)
                else:
                    write(f'Code v{version} :: Successfully Installed {package_name}', 'white', metadata)

    if mode == 'uninstall':
        command = f'{base_c} --uninstall-extension {package_name} --force'
        proc = Popen(mslex.split(command), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        for line in proc.stdout:
            line = line.decode()

            if 'Uninstalling' in line:
                write(f'Code v{version} :: Uninstalling {Fore.MAGENTA}{package_name}{Fore.RESET}', 'green', metadata)

            if 'is not installed' in line:
                write(f'{Fore.GREEN}Code v{version} :: {Fore.MAGENTA}{package_name}{Fore.YELLOW} is not installed!', 'white', metadata)

            if 'was successfully uninstalled' in line:
                write(f'{Fore.GREEN}Code v{version} :: Successfully Uninstalled {Fore.MAGENTA}{package_name}{Fore.RESET}', 'green', metadata)


def handle_sublime_extension(package_name: str, mode: str, metadata: Metadata):
    """
    Installs a sublime text package handling metadata for the method

    #### Arguments
        package_name (str): The name of the sublime text package to be installed
        version (str): The version of the sublime text package to be installed
        mode (str): The method (installation/uninstallation)
        metadata (`Metadata`): Metadata for the method
    """
    if mode == 'install':
        if utils.find_existing_installation('sublime-text-3', 'Sublime Text 3'):
            location = PathManager.get_appdata_directory().replace('\electric', '') + '\Sublime Text 3'
            if os.path.isdir(location) and os.path.isfile(fr'{location}\Packages\User\Package Control.sublime-settings'):
                with open(fr'{location}\Packages\User\Package Control.sublime-settings', 'r') as f:
                    lines = f.readlines()
                    idx = 0
                    for line in lines:
                        if '"Package Control",' in line.strip():
                            idx = lines.index(line)

                    if ']' in lines[idx + 1].strip():
                        lines[idx] = "        \"Package Control\""

                with open(fr'{location}\Packages\User\Package Control.sublime-settings', 'w') as f:
                    f.writelines(lines)

                with open(fr'{location}\Packages\User\Package Control.sublime-settings', 'r') as f:
                    json = js.load(f)
                    current_packages = json['installed_packages']
                    if package_name in current_packages:
                        write(f'{package_name} Is Already Installed!', 'white', metadata)
                        sys.exit()

                    current_packages.append(package_name)
                updated_packages = current_packages
                del json['installed_packages']
                json['installed_packages'] = updated_packages
                with open(fr'{location}\Packages\User\Package Control.sublime-settings', 'w+') as f:
                    f.write(js.dumps(json, indent=4))
                write(f'Successfully Added {package_name} to Sublime Text 3', 'white', metadata)
            else:
                if not os.path.isdir(location):
                    os.mkdir(location)
                if not os.path.isdir(fr'{location}\Installed Packages'):
                    os.mkdir(fr'{location}\Installed Packages')

                # Package Control Not Installed
                with Halo('Installing Package Control', text_color='cyan'):
                    urlretrieve('https://packagecontrol.io/Package%20Control.sublime-package', fr'{location}\Installed Packages\Package Control.sublime-package')

                if not os.path.isdir(fr'{location}\Packages'):
                    os.mkdir(fr'{location}\Packages')
                if not os.path.isdir(fr'{location}\Packages\User'):
                    os.mkdir(fr'{location}\Packages\User')

                with open(fr'{location}\Packages\User\Package Control.sublime-settings', 'w+') as f:
                    f.write(
                        js.dumps({
                        "bootstrapped": True,
                        "installed_packages": [
                            "Package Control"
                        ]},
                        indent=4
                        )
                    )

                handle_sublime_extension(package_name, mode, metadata)
        else:
            click.echo(click.style('Sublime Text 3 Is Not Installed. Exit Code [0112]', fg='bright_yellow'))
            utils.disp_error_msg(utils.get_error_message('0112', 'install', package_name, None), metadata)
            utils.handle_exit('error', metadata)


def handle_atom_package(package_name: str, mode: str, metadata: Metadata):
    """
    Installs an atom package handling metadata

    #### Arguments
        package_name (str): The name of the atom package to be installed
        version (str): The version of the atom package to be installed
        mode (str): The method (installation/uninstallation)
        metadata (`Metadata`): Metadata for the method
    """
    if mode == 'install':
        try:
            proc = Popen('apm --version --no-color'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
            output, err = proc.communicate()
            version = output.decode().splitlines()[0].split()[1]
        except FileNotFoundError:
            print('Atom is not installed')
            sys.exit()
        with Halo(f'apm v{version} :: Installing {package_name}', text_color='cyan') as h:
            proc = Popen(f'apm install {package_name}', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
            for line in proc.stdout:
                line = line.decode()
                if 'failed' in line:
                    h.fail(f' Failed to Install {package_name} to <=> {line.split()[3]}')

                if 'done' in line:
                    h.stop()
                    click.echo(click.style(f' Successfully Installed {package_name} to <=> {line.split()[3]}', 'green'))

        if mode == 'uninstall':
            try:
                proc = Popen('apm --version --no-color'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                output, err = proc.communicate()
                version = output.decode().splitlines()[0].split()[1]
            except FileNotFoundError:
                print('Atom is not installed')
                sys.exit()
            with Halo(f'apm v{version} :: Installing {package_name}', text_color='cyan') as h:
                proc = Popen(f'apm install {package_name}', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
                for line in proc.stdout:
                    line = line.decode()
                    if 'failed' in line:
                        h.fail(f' Failed to Install {package_name} to <=> {line.split()[3]}')

                    if 'done' in line:
                        h.stop()
                        click.echo(click.style(f' Successfully Installed {package_name} to <=> {line.split()[3]}', 'green'))
    if mode == 'uninstall':
        try:
            proc = Popen('apm --version --no-color'.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
            output, _ = proc.communicate()
            version = output.decode().splitlines()[0].split()[1]
        except FileNotFoundError:
            print('Atom is not installed')
            sys.exit()
        with Halo(f'apm v{version} :: Uninstalling {package_name}', text_color='cyan') as h:
            proc = Popen(f'apm deinstall {package_name}', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
            for line in proc.stdout:
                line = line.decode()
                if 'failed' in line:
                    h.fail(f' Failed to Uninstall {package_name}')

                if 'done' in line:
                    h.stop()
                    click.echo(click.style(f' Successfully Uninstalled {package_name}', 'green'))

