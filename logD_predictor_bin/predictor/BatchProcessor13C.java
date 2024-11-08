package predictor;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.FileReader;
import java.io.BufferedReader;
import java.util.Locale;

import org.openscience.cdk.DefaultChemObjectBuilder;
import org.openscience.cdk.interfaces.IAtom;
import org.openscience.cdk.interfaces.IAtomContainer;
import org.openscience.cdk.io.MDLV2000Reader;
import org.openscience.cdk.io.MDLV3000Reader;
import org.openscience.cdk.aromaticity.Aromaticity;
import org.openscience.cdk.aromaticity.ElectronDonation;
import org.openscience.cdk.graph.Cycles;
import org.openscience.nmrshiftdb.PredictionTool;
import org.openscience.nmrshiftdb.util.AtomUtils;

/**
 * The BatchProcessor13C class processes a batch of .mol files to predict 1H NMR chemical shifts.
 * It reads molecular files, applies chemical property detection, and writes the results to CSV files.
 */
public class BatchProcessor13C {

    // Counter to keep track of the number of processed .mol files.
    private static int processedFileCount = 0;

    // ANSI color codes for output formatting.
    private static final String ANSI_GREEN = "\033[38;5;46m";  // Green color code.
    private static final String ANSI_RED = "\033[31m";    // Red color code.
    private static final String ANSI_RESET = "\033[0m";   // Reset color code.

    /**
     * Processes a single .mol file to predict 13C NMR shifts and saves the results to a CSV file.
     * 
     * @param molFile The .mol file to be processed.
     * @param csvFilePath The file path where the CSV file will be saved.
     * @param solvent The solvent used for prediction. Default is "Unreported".
     * @param use3d A flag indicating whether to use 3D molecular data for the prediction.
     */
    private static void processMolFile(File molFile, String csvFilePath, String solvent, boolean use3d) {
        try {
            // Determine whether molFile is V2000 or V3000 format.
            BufferedReader br = new BufferedReader(new FileReader(molFile));
            br.readLine(); // Skip line 1.
            br.readLine(); // Skip line 2.
            br.readLine(); // Skip line 3.
            String line4 = br.readLine();
            br.close();

            IAtomContainer mol = null;

            if (line4 != null && line4.contains("V3000")) {
                // Use MDLV3000Reader for V3000 files.
                MDLV3000Reader mdlreader3000 = new MDLV3000Reader(new FileReader(molFile));
                mol = mdlreader3000.read(DefaultChemObjectBuilder.getInstance().newInstance(IAtomContainer.class));
            } else {
                // Use MDLV2000Reader for V2000 files.
                MDLV2000Reader mdlreader = new MDLV2000Reader(new FileReader(molFile));
                mol = mdlreader.read(DefaultChemObjectBuilder.getInstance().newInstance(IAtomContainer.class));
            }

            // Add hydrogen atoms to the molecular structure.
            AtomUtils.addAndPlaceHydrogens(mol);

            // Apply aromaticity detection to the molecule.
            Aromaticity aromaticity = new Aromaticity(ElectronDonation.cdk(), Cycles.cdkAromaticSet());
            aromaticity.apply(mol);

            // Initialize the NMRShiftDB prediction tool.
            PredictionTool predictor = new PredictionTool();

            // Prepare to write the prediction results to a CSV file.
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(csvFilePath))) {
                // Iterate over all atoms in the molecule.
                for (int i = 0; i < mol.getAtomCount(); i++) {
                    IAtom curAtom = mol.getAtom(i);
                    float[] result = null;

                    // If the current atom is a CARBON atom (atomic number 6), perform prediction.
                    if (curAtom.getAtomicNumber() == 6) {
                        result = predictor.predict(mol, curAtom, use3d, solvent);

                        // Write the predicted NMR shift value to the CSV file if a result is obtained.
                        if (result != null) {
                            writer.write(String.format(Locale.US, "%.2f\n", result[1]));
                        }
                    }
                }
            }

            // Increment the count of processed .mol files.
            processedFileCount++;
        } catch (Exception e) {
            // Print error message in red if file processing fails.
            System.err.println(ANSI_RED + "Error while processing file " + molFile.getName() + ": " + e.getMessage() + ANSI_RESET);
            e.printStackTrace();
        }
    }

    /**
     * Prints a dynamic progress bar with color to indicate progress.
     * 
     * @param current The current file number being processed.
     * @param total   The total number of files to process.
     */
    private static void printProgress(int current, int total) {
        int barLength = 25; // Length of the progress bar.
        int filledLength = (int) (barLength * ((double) current / total));

        // Build the progress bar string with colored blocks.
        StringBuilder bar = new StringBuilder();
        for (int i = 0; i < filledLength; i++) {
            // Add green colored blocks.
            bar.append(ANSI_GREEN).append("█").append(ANSI_RESET);
        }
        for (int i = filledLength; i < barLength; i++) {
            bar.append("-"); // Add dashes for empty space.
        }

        // Calculate percentage completion.
        int percent = (int) (100.0 * current / total);

        // Print the progress bar with the current file/total file count and percentage.
        System.out.print("\rProgress: |" + bar + "| " + current + "/" + total + " (" + percent + "%)");
        System.out.flush();

        // If completed, move to a new line.
        if (current == total) {
            System.out.println(" ");
        }
    }

    /**
     * Main method for batch processing .mol files.
     * 
     * @param args Command-line arguments: 
     *             args[0] - input folder containing .mol files,
     *             args[1] - output folder for CSV files,
     *             args[2] (optional) - solvent for prediction,
     *             args[3] (optional) - "no3d" flag to disable 3D data usage.
     */
    public static void main(String[] args) {
        // Check if the required arguments (input and output folders) are provided.
        if (args.length < 2) {
            System.err.println(ANSI_RED + "Usage: java BatchProcessor1H <inputFolder> <outputFolder> [solvent] [no3d]" + ANSI_RESET);
            System.exit(1);
        }

        // Parse the input and output folder paths.
        File inputFolder = new File(args[0]);
        File outputFolder = new File(args[1]);
        String solvent = "Unreported"; // Default solvent if not specified.
        boolean use3d = true;          // Default to using 3D information.

        // Validate that input and output folders are directories.
        if (!inputFolder.isDirectory() || !outputFolder.isDirectory()) {
            System.err.println(ANSI_RED + "Input or output folder is not a directory." + ANSI_RESET);
            System.exit(1);
        }

        // Parse the optional solvent argument.
        if (args.length >= 3) {
            solvent = args[2];
        }

        // Check for the "no3d" flag to disable 3D data usage.
        if (args.length >= 4 && args[3].equalsIgnoreCase("no3d")) {
            use3d = false;
        }

        // List all .mol files in the input folder.
        File[] molFiles = inputFolder.listFiles((dir, name) -> name.endsWith(".mol"));
        if (molFiles != null && molFiles.length > 0) {
            int totalFiles = molFiles.length; // Total number of .mol files to be processed.
            int counter = 1; // Counter to keep track of the number of processed files.

            // Iterate over each .mol file in the input folder.
            for (File molFile : molFiles) {
                // Construct the file path for the output CSV file.
                String csvFilePath = new File(outputFolder, molFile.getName().replace(".mol", ".csv")).getPath();

                // Display progress bar with color.
                printProgress(counter, totalFiles);

                // Process the current .mol file.
                processMolFile(molFile, csvFilePath, solvent, use3d);
                counter++; // Increment the counter after processing each file.
            }

            // Move to a new line after processing all files.
            System.out.println();

            // Display the total number of processed .mol files in green.
            System.out.println(ANSI_GREEN + "Total number of .mol files processed for 13C NMR prediction: " + processedFileCount + ANSI_RESET);
        } else {
            // Print an error message in red if no .mol files are found in the input folder.
            System.err.println(ANSI_RED + "No .mol files found in the input folder." + ANSI_RESET);
        }
    }
}
