using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Threading;
using System.Net;
using System.Net.Sockets;
using System.Windows.Forms;
using System.Security.Cryptography;
using System.Diagnostics;
using System.Media;
using System.Text.RegularExpressions;
using System.Security.Principal;

namespace cio_launcher
{
    public class Launcher
    {
        /// <summary>
        /// An async task that checks for incoming messages from the server and responds to them.
        /// </summary>
        static async Task Listen(Launcher launcher, CancellationToken token)
        {
            while (!token.IsCancellationRequested)
            {
                string msg = await launcher.sr.ReadLineAsync();
                if (msg != null)
                {
                    // Split the message up into chunks for processing using the delimiter
                    string[] split_msg = msg.Split(Constants.MSG_DELIMITER.ToCharArray());

                    if (split_msg[0] == Constants.SV_SERVER_INFO.ToString() && Globals.current_state == Constants.STATE_VALIDATING)
                    {
                        string server_ver = split_msg[1];
                        if (Constants.LAUNCHER_VER == server_ver)
                        {
                            // We have connected, our launcher is validated, let's fetch the download info
                            Globals.current_state = Constants.STATE_GET_BASE_LINK;
                            Console.WriteLine("Launcher validated.");
                            // Send the dl base link request
                            launcher.sw.WriteLine(Constants.CL_REQ_BASE_LINK.ToString());
                            launcher.sw.Flush();
                        }
                        else
                        {
                            MessageBox.Show("This launcher is out of date. Press OK to be taken to the download page for the new launcher.",
                                "Update Available", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                            if (Constants.IS_DEV)
                                Process.Start(Constants.DEV_INSTALLER);
                            else
                                Process.Start(Constants.DL_PAGE);
                            Application.Exit();
                        }
                    }

                    else if (split_msg[0] == Constants.SV_BASE_LINK.ToString() && Globals.current_state == Constants.STATE_GET_BASE_LINK)
                    {
                        string base_link = split_msg[1];
                        Console.WriteLine("Base link: " + base_link);
                        Globals.dl_base_link = base_link;

                        // Now that we have the base link begin to generate a download list.
                        launcher.lf.ShowStatus(Constants.STATUS_FETCHING);
                        Globals.current_state = Constants.STATE_GEN_DL_LIST;
                        launcher.BeginGenerateDLList();
                    }

                    else if (split_msg[0] == Constants.SV_CREATE_ACC_RESP.ToString() && Globals.current_state == Constants.STATE_ACC_SUBMITTING)
                    {
                        int response = Int32.Parse(split_msg[1]);
                        if (response == 1)
                        {
                            // Account successfully created!
                            Globals.current_state = Constants.STATE_LOGIN_MENU;
                            launcher.lf.ShowAll();
                        }
                        else if (response == 0)
                        {
                            // Account not created! Name already exists.
                            MessageBox.Show("An account with that name already exists.", "Account Already Exists", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                            Globals.current_state = Constants.STATE_ACC_CREATE_MENU;
                            launcher.lf.ShowAll();
                        }
                    }

                    else if (split_msg[0] == Constants.SV_PLAY_RESP.ToString() && Globals.current_state == Constants.STATE_LOGGING_IN)
                    {
                        int response = Int32.Parse(split_msg[1]);
                        if (response == 1)
                        {
                            Console.WriteLine("Accepted!");
                            // Login accepted!
                            string gameServer = split_msg[2];
                            string gameVersion = split_msg[3];
                            string loginToken = "asdasdasbsdf";
                            string username = launcher.lf.GetUsername();

                            // Set the environment variables.
                            Environment.SetEnvironmentVariable("ACCOUNT_NAME", username);
                            Environment.SetEnvironmentVariable("GAME_SERVER", gameServer);
                            Environment.SetEnvironmentVariable("GAME_VERSION", gameVersion);
                            Environment.SetEnvironmentVariable("LOGIN_TOKEN", loginToken);

                            Console.WriteLine("Starting coginvasion.exe");

                            launcher.lf.Hide();
                            launcher.CloseConnection();
                            // Reset our variables for when the launcher opens back up.
                            launcher.PrepareToRestart();

                            ProcessStartInfo ciInfo = new ProcessStartInfo();
                            ciInfo.ErrorDialog = true;
                            ciInfo.UseShellExecute = false;
                            ciInfo.FileName = Directory.GetCurrentDirectory() + "\\coginvasion.exe";
                            ciInfo.WindowStyle = ProcessWindowStyle.Hidden;
                            ciInfo.CreateNoWindow = true;

                            Console.WriteLine("Waiting for exit...");

                            try
                            {
                                Process ciProc = Process.Start(ciInfo);
                                ciProc.WaitForExit();
                                ciProc.Close();
                            }
                            catch (System.ComponentModel.Win32Exception e)
                            {
                                Console.WriteLine(e.Message);
                            }

                            Console.WriteLine("Exited");
                            launcher.DoInitialStuff();

                        }
                        else if (response == 0)
                        {
                            // Login rejected! Invalid credentials.
                            MessageBox.Show("Username and/or password is incorrect.", "Invalid Credentials", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                            Globals.current_state = Constants.STATE_LOGIN_MENU;
                            launcher.lf.ShowAll();
                        }
                        else if (response == 2)
                        {
                            // Login rejected! Banned account.
                            MessageBox.Show("This account has been banned.", "Banned", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                            Globals.current_state = Constants.STATE_LOGIN_MENU;
                            launcher.lf.ShowAll();
                        }
                    }

                    else if (split_msg[0] == Constants.SV_MSG.ToString())
                    {
                        string svMsg = split_msg[1];
                        MessageBox.Show(svMsg, "Message From Server", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                        launcher.lf.HideAll();
                        if (Globals.current_state == Constants.STATE_LOGIN_MENU)
                            Globals.current_state = Constants.STATE_LOGIN_MENU;
                        else if (Globals.current_state == Constants.STATE_ACC_SUBMITTING)
                            Globals.current_state = Constants.STATE_ACC_CREATE_MENU;
                        launcher.lf.ShowAll();
                    }

                }
            }
        }

        public void BeginGenerateDLList()
        {
            // Download the hash file (synchronous)
            Console.WriteLine("Downloading hash file");
            WebClient dlClient = new WebClient();
            dlClient.DownloadDataCompleted += ProcessHashFile;
            dlClient.DownloadDataAsync(new Uri(Globals.dl_base_link + "file_info.txt"));
        }

        private void ProcessHashFile(object sender, DownloadDataCompletedEventArgs e)
        {
            byte[] data = e.Result;
            string strData = System.Text.Encoding.UTF8.GetString(data, 0, data.Length);
            Console.WriteLine("Processing hash file");
            string[] lines = strData.Split('\n');
            foreach (string fileData in lines)
            {
                if (string.IsNullOrWhiteSpace(fileData) || fileData.Substring(0, 2) == "//")
                    continue;

                string[] split_data = fileData.Split(' ');
                string filename = split_data[0];
                string md5 = split_data[1];
                md5 = Regex.Replace(md5, @"\s", "");
                if (!IsSameMD5(filename, md5))
                {
                    Console.WriteLine(filename + " is out of date or missing! Adding to download list.");
                    dl_list.Add(filename);
                }
                else
                    Console.WriteLine(filename + " is up to date!");
            }
            if (dl_list.Count > 0)
            {
                Console.WriteLine("Will download files: ");
                string output = "";
                foreach (string file in dl_list)
                {
                    if (dl_list.IndexOf(file) < dl_list.Count - 1)
                        output += file + ", ";
                    else
                        output += file;
                }
                Console.WriteLine(output);
            }
            else
                Console.WriteLine("All files are up to date!");

            // We're good to go! Show the log-in menu.
            Globals.current_state = Constants.STATE_LOGIN_MENU;
            lf.ShowAll();
        }

        private bool IsSameMD5(string filename, string md5)
        {
            if (!File.Exists(filename))
            {
                return false;
            }
            else
            {
                FileStream fileStream = File.Open(filename, FileMode.Open);
                
                string myMD5 = BitConverter.ToString(new SHA1CryptoServiceProvider().ComputeHash(fileStream));

                Console.WriteLine(filename + ": " + myMD5);

                fileStream.Close();

                return (string.Equals(md5, myMD5));
            }
        }

        public void StartUpdatingFiles()
        {
            lf.ShowLoginLbl();
            lf.ShowDlProgressBar();
            lf.SetLoginLblText(Constants.UPDATING_FILES);
            NextFile();
        }

        public void NextFile()
        {
            currentFile++;
            if (currentFile > dl_list.Count - 1)
            {
                // We're done updating!
                alreadyUpdated = true;
                lf.HideDlProgressBar();
                lf.HideAll();
                Globals.current_state = Constants.STATE_LOGGING_IN;
                lf.ShowStatus(Constants.STATUS_LOGGING);
                lf.SendLoginRequest();
                return;
            }
            string fileName = dl_list[currentFile];
            lf.ShowStatus(string.Format(Constants.STATUS_FILE_DATA, currentFile + 1, dl_list.Count, fileName));
            string fullLink = Globals.dl_base_link + fileName;
            WebClient dlClient = new WebClient();
            dlClient.DownloadDataCompleted += DownloadDataCompleted;
            dlClient.DownloadProgressChanged += DownloadProgressChanged;
            dlClient.DownloadDataAsync(new Uri(fullLink));
        }

        private void DownloadProgressChanged(object sender, DownloadProgressChangedEventArgs e)
        {
            lf.SetDlProgressBarValue(e.ProgressPercentage);
        }

        private void DownloadDataCompleted(object sender, DownloadDataCompletedEventArgs e)
        {
            byte[] data = e.Result;
            string name = dl_list[currentFile];
            File.WriteAllBytes(name, data);
            NextFile();
        }

        public bool HasAlreadyUpdated()
        {
            return alreadyUpdated;
        }

        public void CloseConnection()
        {
            client.Close();
        }

        public Launcher()
        {
            Globals.launcher = this;

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            LoginForm lf = new LoginForm();
            this.lf = lf;
            if (DoInitialStuff())
                Application.Run(lf);
        }

        public bool DoInitialStuff()
        {
            lf.Show();
            lf.HideAll(true);

            var identity = WindowsIdentity.GetCurrent();
            var principal = new WindowsPrincipal(identity);
            if (!principal.IsInRole(WindowsBuiltInRole.Administrator))
            {
                MessageBox.Show("Whoops! You must run the Cog Invasion Online Launcher with administrator rights.",
                    "No Admin", MessageBoxButtons.OK, MessageBoxIcon.Stop);
                return false;
            }

            lf.ShowStatus(Constants.STATUS_CONNECTING);

            string server;
            if (Constants.IS_DEV)
                server = Constants.LOGIN_SERVER_DEV;
            else
                server = Constants.LOGIN_SERVER;

            string gameserver = server + ":" + Constants.LOGIN_PORT.ToString();
            Console.WriteLine("Connecting to login server at " + gameserver);

            // Connect to the server
            TcpClient client = new TcpClient();
            this.client = client;

            try
            {
                client.Connect(server, Constants.LOGIN_PORT);
            }
            catch (SocketException e)
            {
                Console.WriteLine(e.Message);
                Console.WriteLine("Could not connect to the login server.");
                MessageBox.Show("Yikes! It seems the Cog Invasion Online servers are down right now.\nTry again later.",
                    "Could Not Connect", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                return false;
            }

            Console.WriteLine("Connected");

            // Initialize our stream readers and writers for talking to the server
            StreamReader sr = new StreamReader(client.GetStream());
            this.sr = sr;
            StreamWriter sw = new StreamWriter(client.GetStream());
            this.sw = sw;

            List<string> dl_list = new List<string>();
            this.dl_list = dl_list;

            // Start the reader task
            CancellationTokenSource cts = new CancellationTokenSource();
            this.cts = cts;
            var listen_task = Listen(this, cts.Token);
            

            Console.WriteLine("Now sending server info req");

            // We are now validating our launcher
            lf.ShowStatus(Constants.STATUS_VALIDATING);
            Globals.current_state = Constants.STATE_VALIDATING;
            // Send the server info req
            sw.WriteLine(Constants.CL_SERVER_INFO.ToString());
            sw.Flush();

            return true;
        }

        public void PrepareToRestart()
        {
            cts.Cancel();
            cts = null;
            sr.Close();
            sr = null;
            sw.Close();
            sw = null;
            client.Close();
            client = null;
            dl_list.Clear();
            alreadyUpdated = false;
            Globals.dl_base_link = "";
            currentFile = -1;
        }

        private TcpClient client;
        public StreamReader sr;
        public StreamWriter sw;
        private CancellationTokenSource cts;
        private LoginForm lf;
        private List<string> dl_list;

        private int currentFile = -1;
        private int filesDownloaded = 0;
        private bool alreadyUpdated = false;

    }
}
