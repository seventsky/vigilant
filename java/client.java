import java.io.*;
import java.net.*;


public class BuddyClient {
    public static void main(String[] args) throws IOException {
        Socket socket = new Socket("localhost", 9999);
        BufferedReader doServidor = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        PrintWriter paraServidor = new PrintWriter(socket.getOutputStream(), true);
        BufferedReader doTeclado = new BufferedReader(new InputStreamReader(System.in));

        System.out.println(doServidor.readLine()); // "apelido?"
        String apelido = doTeclado.readLine();
        paraServidor.println(apelido);

        Thread ouvinte = new Thread(() -> {
            try {
                String linha;
                while ((linha = doServidor.readLine()) != null) {
                    System.out.println(linha);
                }
            } catch (IOException e) {
                System.out.println("[conexao encerrada]");
            }
        });
        ouvinte.setDaemon(true);
        ouvinte.start();

        String linha;
        while ((linha = doTeclado.readLine()) != null) {
            paraServidor.println(linha);
        }
    }
}
