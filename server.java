import java.io.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.*;

public class BuddyServer {
    static final int PORTA = 9999;
    static Map<String, PrintWriter> conectados = new ConcurrentHashMap<>();

    public static void main(String[] args) throws IOException {
        imprimirBanner();
        ServerSocket servidor = new ServerSocket(PORTA);
        System.out.println("[servidor] esperando gente conectar na porta " + PORTA + "...");
        while (true) {
            Socket cliente = servidor.accept();
            new Thread(() -> tratarCliente(cliente)).start();
        }
    }

    static void tratarCliente(Socket socket) {
        String apelido = null;
        try {
            BufferedReader entrada = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            PrintWriter saida = new PrintWriter(socket.getOutputStream(), true);

            saida.println("apelido?");
            apelido = entrada.readLine();
            if (apelido == null || apelido.isBlank()) {
                socket.close();
                return;
            }
            if (conectados.containsKey(apelido)) {
                saida.println("foi mal, tenta outro ai.");
                socket.close();
                return;
            }

            conectados.put(apelido, saida);
            avisarTodos("* " + apelido + " entrou *");
            listarConectados(saida);
            saida.println("dicas: /status <texto>  |  /cutucar <apelido>  |  /lista");

            String linha;
            while ((linha = entrada.readLine()) != null) {
                if (linha.startsWith("/cutucar ")) {
                    String alvo = linha.substring(9).trim();
                    PrintWriter destinatario = conectados.get(alvo);
                    if (destinatario != null) {
                        destinatario.println("*** " + apelido + " te cutucou! ***");
                    } else {
                        saida.println("(nao achei ninguem com esse apelido online)");
                    }
                } else if (linha.startsWith("/status ")) {
                    avisarTodos(apelido + " agora esta: " + linha.substring(8));
                } else if (linha.equals("/lista")) {
                    listarConectados(saida);
                } else if (!linha.isBlank()) {
                    avisarTodos(apelido + " diz: " + linha);
                }
            }
        } catch (IOException e) {
            // conexao caiu, sem drama
        } finally {
            if (apelido != null) {
                conectados.remove(apelido);
                avisarTodos("* " + apelido + " saiu *");
            }
        }
    }

    static void avisarTodos(String mensagem) {
        System.out.println(mensagem);
        for (PrintWriter p : conectados.values()) {
            p.println(mensagem);
        }
    }

    static void listarConectados(PrintWriter saida) {
        saida.println("--- online agora (" + conectados.size() + ") ---");
        for (String nome : conectados.keySet()) {
            saida.println("  * " + nome);
        }
        saida.println("-------------------------");
    }

    static void imprimirBanner() {
        System.out.println("=========================================");
        System.out.println("   BuddyServer.java -- lista de contatos");
        System.out.println("   (aperta ctrl+c pra derrubar o servidor)");
        System.out.println("=========================================");
    }
}
