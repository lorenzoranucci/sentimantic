package it.unipg.lorenzoranucci;


import org.apache.commons.text.StringEscapeUtils;
import org.jsoup.Jsoup;
import org.jsoup.safety.Whitelist;

import java.io.*;
import java.net.URISyntaxException;
import java.nio.charset.Charset;
import java.util.regex.Pattern;

/**
 * Created by lorenzo on 05/02/18.
 */
public class Main {

    private static File destinationFolder;
    private static PrintWriter currentPrintWriter=null;
    private static int outputFilesCounter=1;
    private static Integer maxFileSizeMB=null;
    private static File currentOutFile=null;


    public static void main(String[] args) throws URISyntaxException, IOException {
        if(args.length>2){
            maxFileSizeMB=Integer.parseInt(args[2]);
        }

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
        createOutputFileAndWriter();
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
                documentWriting=false;
            }

            if(startTagFound){
                String[] split=line.split("<\\s*doc .*id=\"");
                String id=split[1].split("\"")[0];
                openDocument(id);
                documentWriting=true;
            }

            if(documentWriting && !startTagFound && !endTagFound)
                writeLine(line);

        }

        closeOutputFileAndWriter();
    }

    private static void createOutputFileAndWriter() throws IOException {
        currentOutFile=new File(destinationFolder.getPath()+File.separator+"out"+outputFilesCounter+".xml");
        currentOutFile.createNewFile();
        currentPrintWriter=new PrintWriter(new OutputStreamWriter(new FileOutputStream(currentOutFile), Charset.forName("UTF-8")));
        currentPrintWriter.println("<dump"+outputFilesCounter+">");
        currentPrintWriter.flush();
    }

    private static void closeOutputFileAndWriter() throws IOException {
        currentPrintWriter.println("</dump"+outputFilesCounter+">");
        currentPrintWriter.flush();
        currentPrintWriter.close();
    }

    private static void openDocument(String id) throws IOException {
        if(maxFileSizeMB!=null && (currentOutFile.length()/1000000)>maxFileSizeMB){
            closeOutputFileAndWriter();
            outputFilesCounter++;
            createOutputFileAndWriter();
        }
        currentPrintWriter.println("<document>");
        currentPrintWriter.println("\t<id>"+id+"</id>");
        currentPrintWriter.println("\t<text>");
        currentPrintWriter.flush();
    }

    private static void writeLine(String line){
        if(currentPrintWriter!=null ) {
            String lineHtmlRemoved= Jsoup.clean(line, new Whitelist());
            String escapedLine = StringEscapeUtils.escapeXml11(lineHtmlRemoved);
            currentPrintWriter.println(escapedLine);
            currentPrintWriter.flush();
        }
    }

    private static void closeDocument(){
        if(currentPrintWriter!=null ) {
            currentPrintWriter.println("\t</text>");
            currentPrintWriter.println("\t</document>");
        }

    }
}
