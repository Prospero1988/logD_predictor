import os
import subprocess
import platform

def run_java_batch_processor(mol_directory, predictor, quiet=False):
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
    # Defining the function that controls printing
    def verbose_print(*args, **kwargs):
        if not quiet:
            print(*args, **kwargs)

    # ANSI color
    COLORS = ['\033[38;5;46m',    # Green
              '\033[38;5;196m',   # Red
              '\033[38;5;214m'    # Orange
             ]
    RESET = '\033[0m'

    csv_output_folder = os.path.join(os.getcwd(), f"predicted_spectra_{predictor}")

    if not os.path.exists(csv_output_folder):
        os.makedirs(csv_output_folder)
        verbose_print(f"\nCreated directory: {COLORS[2]}{csv_output_folder}{RESET}")

    # Dynamic separator for classpath depending on operating system
    classpath_separator = ";" if platform.system() == "Windows" else ":"

    # Set the current directory to logD_predictor_bin
    current_dir = os.path.join(os.getcwd(), "logD_predictor_bin")

    # Use os.path.join for platform-independent paths
    if predictor == "1H":
        predictor_jar = os.path.join(current_dir, "predictor", "predictorh.jar")
        cdk_jar = os.path.join(current_dir, "predictor", "cdk-2.9.jar")
        batch_processor_java = os.path.join(current_dir, "predictor", "BatchProcessor1H.java")
        batch_processor_class = "predictor.BatchProcessor1H"
    elif predictor == "13C":
        predictor_jar = os.path.join(current_dir, "predictor", "predictorc.jar")
        cdk_jar = os.path.join(current_dir, "predictor", "cdk-2.9.jar")
        batch_processor_java = os.path.join(current_dir, "predictor", "BatchProcessor13C.java")
        batch_processor_class = "predictor.BatchProcessor13C"

    # Revised javac command for cross-platform
    compile_command = (
        f'javac -classpath "{predictor_jar}{classpath_separator}{cdk_jar}{classpath_separator}{current_dir}" '
        f'-d "{current_dir}" -Xlint:-options -Xlint:deprecation -proc:none "{batch_processor_java}"'
    )

    try:
        subprocess.run(compile_command, shell=True, check=True, cwd=current_dir)
        verbose_print(f"\nSuccessfully compiled {batch_processor_class}.")
        print("\nSpectra prediction in progress...\n")
    except subprocess.CalledProcessError as e:
        print(f"{COLORS[1]}Failed to compile {batch_processor_java}: {e}{RESET}")
        return

    # Revised java command for cross-platform
    run_command = (
        f'java -Xmx1g -classpath "{predictor_jar}{classpath_separator}{cdk_jar}{classpath_separator}{current_dir}" '
        f'{batch_processor_class} "{mol_directory}" "{csv_output_folder}" '
        '"Dimethylsulphoxide-D6 (DMSO-D6, C2D6SO)"'
    )

    try:
        subprocess.run(run_command, shell=True, check=True, cwd=current_dir)
    except subprocess.CalledProcessError as e:
        print(f"{COLORS[1]}Failed to run {batch_processor_class}: {e}{RESET}")

    return csv_output_folder
