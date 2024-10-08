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
 * The BatchProcessor13C class processes a batch of .mol files to predict 13C NMR chemical shifts.
 * It reads molecular files, applies chemical property detection, and writes the results to CSV files.
 */
public class BatchProcessor13C {

    // Counter to keep track of the number of processed .mol files.
    private static int processedFileCount = 0;

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
            // Determine whether molFile is V2000 or V3000
            BufferedReader br = new BufferedReader(new FileReader(molFile));
            br.readLine(); // skip line1
            br.readLine(); // skip line2
            br.readLine(); // skip line3
            String line4 = br.readLine();
            br.close();

            IAtomContainer mol = null;

            if (line4 != null && line4.contains("V3000")) {
                // Use MDLV3000Reader
                MDLV3000Reader mdlreader3000 = new MDLV3000Reader(new FileReader(molFile));
                mol = (IAtomContainer) mdlreader3000.read(DefaultChemObjectBuilder.getInstance().newInstance(IAtomContainer.class));
            } else {
                // Use MDLV2000Reader
                MDLV2000Reader mdlreader = new MDLV2000Reader(new FileReader(molFile));
                mol = (IAtomContainer) mdlreader.read(DefaultChemObjectBuilder.getInstance().newInstance(IAtomContainer.class));
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

                    // If the current atom is a carbon atom (atomic number 6), perform prediction.
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
            // Print error message if file processing fails.
            System.err.println("Error while processing file " + molFile.getName() + ": " + e.getMessage());
            e.printStackTrace();
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
            System.err.println("Usage: java BatchProcessor1H <inputFolder> <outputFolder> [solvent] [no3d]");
            System.exit(1);
        }

        // Parse the input and output folder paths.
        File inputFolder = new File(args[0]);
        File outputFolder = new File(args[1]);
        String solvent = "Unreported"; // Default solvent if not specified.
        boolean use3d = true; // Default to using 3D information.

        // Validate that input and output folders are directories.
        if (!inputFolder.isDirectory() || !outputFolder.isDirectory()) {
            System.err.println("Input or output folder is not a directory.");
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
        if (molFiles != null) {
            int totalFiles = molFiles.length; // Total number of .mol files to be processed.
            int counter = 1; // Counter to keep track of the number of processed files.
            int previousLineLength = 0; // Used to maintain the length of the progress message.

            // Iterate over each .mol file in the input folder.
            for (File molFile : molFiles) {
                // Construct the file path for the output CSV file.
                String csvFilePath = new File(outputFolder, molFile.getName().replace(".mol", ".csv")).getPath();

                // Build and print the progress message.
                String message = "Processing " + counter + "/" + totalFiles + ": " + molFile.getName();
                int messageLength = message.length();
                
                // Adjust message length by adding padding if the current message is shorter than the previous one.
                if (messageLength < previousLineLength) {
                    int paddingLength = previousLineLength - messageLength;
                    String padding = new String(new char[paddingLength]).replace('\0', ' ');
                    message += padding;
                }

                // Update the previousLineLength for the next iteration.
                previousLineLength = message.length();

                // Print the progress message, overwriting the previous line.
                System.out.print("\r" + message);
                System.out.flush();

                // Process the current .mol file.
                processMolFile(molFile, csvFilePath, solvent, use3d);
                counter++; // Increment the counter after processing each file.
            }

            // Move to a new line after processing all files.
            System.out.println();

            // Display the total number of processed .mol files.
            System.out.println("\nTotal number of .mol files processed for 13C NMR prediction: " + processedFileCount);
        } else {
            // Print an error message if no .mol files are found in the input folder.
            System.err.println("No .mol files found in the input folder.");
        }
    }
}
