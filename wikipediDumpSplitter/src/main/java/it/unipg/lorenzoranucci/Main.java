package it.unipg.lorenzoranucci;


import org.apache.commons.text.StringEscapeUtils;

import java.io.*;
import java.net.URISyntaxException;
import java.util.regex.Pattern;

/**
 * Created by lorenzo on 05/02/18.
 */
public class Main {

    private static File destinationFolder;
    private static PrintWriter currentPrintWriter=null;

    public static void main(String[] args) throws URISyntaxException, IOException {
        String destinationFolderPath=args[1];
        destinationFolder=new File(destinationFolderPath);
        destinationFolder.mkdirs();

        String dumpXmlFileArg=args[0];
        File dumpXmlFile=new File(dumpXmlFileArg);
        BufferedReader dumpBufferedReader=new BufferedReader(new FileReader(dumpXmlFile));

        String line;
        final Pattern startTagPattern = Pattern.compile("<\\s*doc .*id=\"");
        final Pattern endTagPattern = Pattern.compile("<\\s*\\/doc\\s*>");
        boolean documentWriting=false;
        while((line=dumpBufferedReader.readLine())!=null){
            boolean startTagFound=false;
            boolean endTagFound=false;
            if(startTagPattern.matcher(line).find()){
                startTagFound=true;
            }
            else if(documentWriting && endTagPattern.matcher(line).find()){
                endTagFound=true;
            }

            if(documentWriting && (endTagFound || startTagFound)){
                closeDocument();
            }

            if(startTagFound){
                String[] split=line.split("<\\s*doc .*id=\"");
                String id=split[1].split("\"")[0];
                createDocument(id);
                documentWriting=true;
            }

            if(documentWriting && !startTagFound && !endTagFound)
                writeLine(line);

        }

    }

    private static void createDocument(String id){
        currentPrintWriter=null;
        File currentDocumentFile=new File(destinationFolder.getPath()+File.separator+id+".xml");
        try {
            currentDocumentFile.createNewFile();
        } catch (IOException e) {
            e.printStackTrace();
        }
        try {
            currentPrintWriter=new PrintWriter(new BufferedWriter(new FileWriter(currentDocumentFile)));
            currentPrintWriter.println("<document>");
            currentPrintWriter.println("\t<id>"+id+"</id>");
            currentPrintWriter.println("\t<text>");
            currentPrintWriter.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void writeLine(String line){
        if(currentPrintWriter!=null ) {
            String escapedLine = StringEscapeUtils.escapeXml11(StringEscapeUtils.escapeHtml4(line));
            currentPrintWriter.println(escapedLine);
            currentPrintWriter.flush();
        }
    }

    private static void closeDocument(){
        if(currentPrintWriter!=null ) {
            currentPrintWriter.println("\t</text>");
            currentPrintWriter.println("\t</document>");
            currentPrintWriter.close();
            currentPrintWriter=null;
        }
    }
}
