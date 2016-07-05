using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using Newtonsoft.Json;
using System.Security.Cryptography;

namespace cio_login_server
{
    static class Constants
    {
        public const int CL_REQ_SERVER_INFO = 1;
        public const int SV_SERVER_INFO = 2;
        public const int CL_REQ_PLAY = 3;
        public const int CL_REQ_BASE_LINK = 4;
        public const int SV_BASE_LINK = 5;
        public const int CL_REQ_CREATE_ACC = 6;
        public const int SV_CREATE_ACC_RESP = 7;
        public const int SV_PLAY_RESP = 8;
        public const int SV_MSG = 9;
        public static string LAUNCHER_VER = Environment.GetEnvironmentVariable("LAUNCHER_VER");
        public const string MSG_DELIMITER = ";";
        public const string DL_BASE_LINK = "http://download.coginvasion.com/";
        public const string DB_FILE = "database/AccData.json";
        public static int ACC_LIMIT_PER_COMP = Int32.Parse(Environment.GetEnvironmentVariable("ACC_LIMIT_PER_COMP"));
        public static int ACCOUNT_LIMIT = Int32.Parse(Environment.GetEnvironmentVariable("ACCOUNT_LIMIT"));

        public const string MSG_TMAOTC = "At this time, only {0} account(s) can be created on each computer.";
        public const string MSG_TMAIT = "At this time, Cog Invasion Online only allows a total of {0} game account(s) to be created. This limit has already been reached. We apologize for the inconvenience.";

        public const string FAIL = "0";
        public const string SUCCESS = "1";

        public static string GAME_SERVER = Environment.GetEnvironmentVariable("GAME_SERVER");
        public static string SERVER_VERSION = Environment.GetEnvironmentVariable("GAME_VERSION");
    }

    class Client
    {
        public Client(Server server, List<Client> clients, TcpClient client, StreamReader sr, StreamWriter sw, string ip)
        {
            this.server = server;
            this.client = client;
            this.sr = sr;
            this.sw = sw;
            this.ip = ip;
            client_list = clients;

            // Start processing this client
            cts = new CancellationTokenSource();
            var proctask = Process(cts.Token);
        }

        public async Task Process(CancellationToken token)
        {
            while (!token.IsCancellationRequested)
            {
                try
                {
                    string request =  await sr.ReadLineAsync();
                    string[] split_msg = request.Split(Constants.MSG_DELIMITER.ToCharArray());

                    if (split_msg[0] == Constants.CL_REQ_SERVER_INFO.ToString())
                    {
                        Console.WriteLine("Client requested server info.");
                        Console.WriteLine("Server Version: " + Constants.LAUNCHER_VER);
                        string msg = Constants.SV_SERVER_INFO.ToString() + Constants.MSG_DELIMITER + Constants.LAUNCHER_VER;
                        sw.WriteLine(msg);
                        sw.Flush();
                    }

                    else if (split_msg[0] == Constants.CL_REQ_BASE_LINK.ToString())
                    {
                        Console.WriteLine("Got base link request");
                        sw.WriteLine(Constants.SV_BASE_LINK.ToString() + Constants.MSG_DELIMITER + Constants.DL_BASE_LINK);
                        sw.Flush();
                    }

                    else if (split_msg[0] == Constants.CL_REQ_PLAY.ToString())
                    {
                        Console.WriteLine("Got a play request.");
                        string username = split_msg[1].ToLower();
                        string password = split_msg[2];
                        Console.WriteLine("Username: " + username + ", Passsword: " + password);
                        string loginResp = Constants.SV_PLAY_RESP.ToString() + Constants.MSG_DELIMITER;
                        if (server.AccNameExists(username))
                        {
                            Account acc = server.GetAccountByName(username);
                            string accPHash = acc.Password;
                            if (Server.HashPasswordSHA256(password) == accPHash)
                                loginResp += Constants.SUCCESS;
                            else
                                loginResp += Constants.FAIL;
                        }
                        else
                            loginResp += Constants.FAIL;
                        loginResp += Constants.MSG_DELIMITER + Constants.GAME_SERVER + Constants.MSG_DELIMITER + Constants.SERVER_VERSION;
                        sw.WriteLine(loginResp);
                        sw.Flush();
                    }

                    else if (split_msg[0] == Constants.CL_REQ_CREATE_ACC.ToString())
                    {
                        string username = split_msg[1].ToLower();
                        string password = split_msg[2];
                        string mac = split_msg[3];

                        Console.WriteLine("Attemping to create account with username: " + username + ", Password: " + password);

                        string msg = string.Empty;

                        if (server.AccNameExists(username))
                        {
                            Console.WriteLine("This account name already exists.");
                            msg = Constants.SV_CREATE_ACC_RESP.ToString() + Constants.MSG_DELIMITER + Constants.FAIL;
                        }
                        else if (!server.CanMakeNewAcc(mac))
                        {
                            Console.WriteLine("Too many accounts on this MAC address.");
                            msg = Constants.SV_MSG.ToString() + Constants.MSG_DELIMITER + string.Format(Constants.MSG_TMAOTC, Constants.ACC_LIMIT_PER_COMP.ToString());
                        }
                        else if (server.IsTotalAccountLimitReached())
                        {
                            Console.WriteLine("The game's total acc limit has been reached.");
                            msg = Constants.SV_MSG.ToString() + Constants.MSG_DELIMITER + string.Format(Constants.MSG_TMAIT, Constants.ACCOUNT_LIMIT.ToString());
                        }
                        else
                        {
                            // We're good to make the account.
                            string passwordHashed = Server.HashPasswordSHA256(password);
                            Console.WriteLine("Hashed password.");
                            Account acc = new Account();
                            acc.Username = username;
                            acc.Password = passwordHashed;
                            acc.Mac = mac;
                            server.AddAccount(acc);
                            msg = Constants.SV_CREATE_ACC_RESP.ToString() + Constants.MSG_DELIMITER + Constants.SUCCESS;
                        }

                        sw.WriteLine(msg);
                        sw.Flush();
                    
                    }

                }
                catch (Exception)
                {
                    Console.WriteLine("-------LOST CONNECTION-------");
                    Console.WriteLine("IP Address: " + ip);
                    Console.WriteLine("Number of active connections: " + (client_list.Count - 1).ToString());

                    // Stop our async Process task
                    cts.Cancel();

                    client_list.Remove(this);
                }
            }
        }

        private TcpClient client;
        private StreamReader sr;
        private StreamWriter sw;
        private List<Client> client_list;
        private Server server;
        private string ip;
        private CancellationTokenSource cts;
    }

    class Server
    {
        public Server()
        {
            Console.WriteLine("Launcher version: " + Constants.LAUNCHER_VER);
            Console.WriteLine("Game version: " + Constants.SERVER_VERSION);
            Console.WriteLine("Game server: " + Constants.GAME_SERVER);
            Console.WriteLine("Game account limit: " + Constants.ACCOUNT_LIMIT);
            Console.WriteLine("Account limit per comp: " + Constants.ACC_LIMIT_PER_COMP);
            Console.WriteLine("----------------------------------------------");

            listener = new TcpListener(IPAddress.Any, 7033);
            listener.Start();

            CancellationTokenSource cts = new CancellationTokenSource();

            // A list of clients
            clients = new List<Client>();

            SetupJSONData();

            var task = AcceptTcpClients(cts.Token);

            Console.WriteLine("Cog Invasion Online login server running.\n");

            // MAINLOOP:
            while (true)
            {
                Thread.Sleep(4);
            }
        }

        public void AddAccount(Account acc)
        {
            jsonAccounts.Add(acc);
            UpdateDBFile();
        }

        public void UpdateDBFile()
        {
            string newData = JsonConvert.SerializeObject(jsonAccounts);
            File.WriteAllText(Constants.DB_FILE, newData);
        }

        public bool CanMakeNewAcc(string mac)
        {
            int numAccsWithThisMac = 0;
            foreach (Account acc in jsonAccounts)
            {
                if (acc.Mac == mac)
                    numAccsWithThisMac++;
            }
            if (numAccsWithThisMac < Constants.ACC_LIMIT_PER_COMP)
                return true;
            else
                return false;
        }

        public bool IsTotalAccountLimitReached()
        {
            if (jsonAccounts.Count >= Constants.ACCOUNT_LIMIT)
                return true;
            else
                return false;
        }

        public bool AccNameExists(string accName)
        {
            foreach (Account acc in jsonAccounts)
            {
                if (acc.Username == accName)
                    return true;
            }
            return false;
        }

        public static string HashPasswordSHA256(string password)
        {
            byte[] bytes = Encoding.UTF8.GetBytes(password);
            SHA256Managed hashstring = new SHA256Managed();
            byte[] hash = hashstring.ComputeHash(bytes);
            string hashString = string.Empty;
            foreach (byte x in hash)
            {
                hashString += string.Format("{0:x2}", x);
            }
            return hashString;
        }

        public Account GetAccountByName(string username)
        {
            foreach (Account acc in jsonAccounts)
            {
                if (acc.Username == username)
                    return acc;
            }
            return null;
        }

        async Task AcceptTcpClients(CancellationToken token)
        {
            while (!token.IsCancellationRequested)
            {
                var ws = await listener.AcceptTcpClientAsync();
                IPEndPoint endpoint = (IPEndPoint)ws.Client.RemoteEndPoint;
                string ip = endpoint.ToString();
                StreamReader sr = new StreamReader(ws.GetStream());
                StreamWriter sw = new StreamWriter(ws.GetStream());
                Console.WriteLine("-------NEW CONNECTION-------");
                Console.WriteLine("IP Address: " + ip);
                Console.WriteLine("Number of active connections: " + (clients.Count + 1).ToString());
                clients.Add(new Client(this, clients, ws, sr, sw, ip));
            }
        }

        private void SetupJSONData()
        {
            StreamReader dbFileStream = File.OpenText(Constants.DB_FILE);
            jsonAccounts = JsonConvert.DeserializeObject<List<Account>>(dbFileStream.ReadToEnd());
            dbFileStream.Close();
        }

        private List<Client> clients;
        private TcpListener listener;
        private List<Account> jsonAccounts;
    }

    class Program
    {

        static void Main(string[] args)
        {
            new Server();
        }

    }
}
