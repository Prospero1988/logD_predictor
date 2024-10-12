# predictor.py

import os
import subprocess


def run_java_batch_processor(mol_directory, predictor):
    """
    Compiles and runs the Java BatchProcessor for NMR spectrum prediction
    on the specified directory containing .mol files.

    Parameters:
    - mol_directory (str): Path to the input directory containing .mol files.
    - predictor (str): Type of NMR predictor ('1H' or '13C') to use.

    Returns:
    - csv_output_folder (str): Path to the directory where the predicted CSV
                               files are stored.
    """
    
    # ANSI color
    COLORS = ['\033[38;5;46m',
              '\033[38;5;196m'
             ]
    RESET = '\033[0m'
    
    csv_output_folder = os.path.join(os.getcwd(),
                                     f"predicted_spectra_{predictor}")

    if not os.path.exists(csv_output_folder):
        os.makedirs(csv_output_folder)
        print(f"\nCreated directory: {csv_output_folder}")

    if predictor == "1H":
        predictor_jar = ".\\predictor\\predictorh.jar"
        cdk_jar = ".\\predictor\\cdk-2.9.jar"
        batch_processor_java = ".\\predictor\\BatchProcessor1H.java"
        batch_processor_class = "predictor.BatchProcessor1H"
    elif predictor == "13C":
        predictor_jar = ".\\predictor\\predictorc.jar"
        cdk_jar = ".\\predictor\\cdk-2.9.jar"
        batch_processor_java = ".\\predictor\\BatchProcessor13C.java"
        batch_processor_class = "predictor.BatchProcessor13C"

    compile_command = (
        f'javac -classpath "{predictor_jar};{cdk_jar};." -d . '
        f'-Xlint:-options -Xlint:deprecation -proc:none {batch_processor_java}'
    )

    try:
        subprocess.run(compile_command, shell=True, check=True)
        print(f"\n{COLORS[0]}Successfully compiled {batch_processor_class}.{RESET}")
        print("\nSpectra prediction in progress...\n")
    except subprocess.CalledProcessError as e:
        print(f"{COLORS[1]}Failed to compile {batch_processor_java}: {e}{RESET}")
        return

    run_command = (
        f'java -Xmx1g -classpath "{predictor_jar};{cdk_jar};.;./predictor" '
        f'{batch_processor_class} "{mol_directory}" "{csv_output_folder}" '
        '"Dimethylsulphoxide-D6 (DMSO-D6, C2D6SO)"'
    )

    try:
        subprocess.run(run_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"{COLORS[1]}Failed to run {batch_processor_class}: {e}{RESET}")

    return csv_output_folder