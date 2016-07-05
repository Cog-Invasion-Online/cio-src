using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Windows.Forms;
using System.IO;

namespace cio_launcher
{
    public partial class LoginForm : Form
    {
        public LoginForm()
        {
            InitializeComponent();

            var pos = this.PointToScreen(this.login_lbl.Location);
            pos = this.bg_image.PointToClient(pos);
            this.login_lbl.Parent = this.bg_image;
            this.login_lbl.Location = pos;
            this.login_lbl.BackColor = System.Drawing.Color.Transparent;

            var pos2 = this.PointToScreen(this.username_lbl.Location);
            pos2 = this.bg_image.PointToClient(pos2);
            this.username_lbl.Parent = this.bg_image;
            this.username_lbl.Location = pos2;
            this.username_lbl.BackColor = System.Drawing.Color.Transparent;

            var pos3 = this.PointToScreen(this.password_lbl.Location);
            pos3 = this.bg_image.PointToClient(pos3);
            this.password_lbl.Parent = this.bg_image;
            this.password_lbl.Location = pos3;
            this.password_lbl.BackColor = System.Drawing.Color.Transparent;

            var pos4 = this.PointToScreen(this.status_lbl.Location);
            pos4 = this.bg_image.PointToClient(pos4);
            this.status_lbl.Parent = this.bg_image;
            this.status_lbl.Location = pos4;
            this.status_lbl.BackColor = System.Drawing.Color.Transparent;
        }

        private void HandleCreateAccOrLoginStuff()
        {
            string username = this.username_entry.Text;
            string password = this.password_entry.Text;
            StreamWriter sw = Globals.launcher.sw;

            if (Globals.current_state == Constants.STATE_LOGIN_MENU)
            {
                // Log in

                HideAll();
                if (!Globals.launcher.HasAlreadyUpdated())
                {
                    Globals.current_state = Constants.STATE_UPDATE_FILES;
                    Globals.launcher.StartUpdatingFiles();
                }
                else
                {
                    Globals.current_state = Constants.STATE_LOGGING_IN;
                    ShowStatus(Constants.STATUS_LOGGING);
                    SendLoginRequest();
                }
            }
            else if (Globals.current_state == Constants.STATE_ACC_CREATE_MENU)
            {
                // Submit account
                if (string.IsNullOrWhiteSpace(username) || username.Length < 5 ||
                    username.ToLower() == password.ToLower() ||
                    string.IsNullOrWhiteSpace(password) || password.Length < 5 ||
                    username.Contains(Constants.MSG_DELIMITER) || password.Contains(Constants.MSG_DELIMITER))
                {
                    MessageBox.Show("Follow these guidelines for your account info:\n- Username and password " +
                        "must be at least 5 characters long\n- No blank or whitespace entries\n- Username cannot " +
                        "be identical to password\n- Neither username nor password can contain a semicolon (;)",
                        "Bad Entries", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                    return;
                }

                HideAll();
                ShowStatus(Constants.STATUS_SUBMIT);
                Globals.current_state = Constants.STATE_ACC_SUBMITTING;

                string msg = Constants.CL_REQ_CREATE_ACC.ToString() + Constants.MSG_DELIMITER + username +
                    Constants.MSG_DELIMITER + password + Constants.MSG_DELIMITER +
                    Globals.GetMacAddress();
                sw.WriteLine(msg);
                sw.Flush();
            }
        }

        private void play_btn_Click(object sender, EventArgs e)
        {
            HandleCreateAccOrLoginStuff();
        }

        private void create_acc_btn_Click(object sender, EventArgs e)
        {
            HideAll();
            Globals.current_state = Constants.STATE_ACC_CREATE_MENU;
            ShowAll();
        }

        private void back_btn_Click(object sender, EventArgs e)
        {
            HideAll();
            Globals.current_state = Constants.STATE_LOGIN_MENU;
            ShowAll();
        }

        private void username_entry_KeyUp(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter)
                HandleCreateAccOrLoginStuff();
        }

        private void password_entry_KeyUp(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.Enter)
                HandleCreateAccOrLoginStuff();
        }

        private void contact_btn_Click(object sender, EventArgs e)
        {
            Process.Start(Constants.CONTACT_LINK);
        }

        public void HideAll(bool IMeanAll = false)
        {
            this.login_lbl.Hide();
            this.username_lbl.Hide();
            this.password_lbl.Hide();
            this.play_btn.Hide();
            this.username_entry.Hide();
            this.password_entry.Hide();
            if (!IMeanAll)
            {
                if (Globals.current_state == Constants.STATE_LOGIN_MENU)
                    this.create_acc_btn.Hide();
                else if (Globals.current_state == Constants.STATE_ACC_CREATE_MENU)
                    this.back_btn.Hide();
            }
            else
            {
                this.create_acc_btn.Hide();
                this.back_btn.Hide();
            }
        }

        public void ShowAll()
        {
            this.login_lbl.Show();
            this.username_lbl.Show();
            this.password_lbl.Show();
            this.play_btn.Show();
            this.username_entry.Show();
            this.password_entry.Show();
            if (Globals.current_state == Constants.STATE_LOGIN_MENU)
            {
                this.login_lbl.Text = "Log-In";
                this.play_btn.Text = "Play";
                this.create_acc_btn.Show();
            }
            else if (Globals.current_state == Constants.STATE_ACC_CREATE_MENU)
            {
                this.login_lbl.Text = "Create An Account";
                this.play_btn.Text = "Done";
                this.back_btn.Show();
            }
            HideStatus();
        }

        public void ShowStatus(string status)
        {
            this.status_lbl.Text = status;
            this.status_lbl.Show();
            Update();
        }

        public void HideStatus()
        {
            this.status_lbl.Hide();
        }

        public void SetLoginLblText(string text)
        {
            this.login_lbl.Text = text;
        }

        public void ShowLoginLbl()
        {
            this.login_lbl.Show();
        }

        public void SendLoginRequest()
        {
            StreamWriter sw = Globals.launcher.sw;
            string username = username_entry.Text;
            string password = password_entry.Text;
            string msg = Constants.CL_REQ_PLAY.ToString() + Constants.MSG_DELIMITER + username + Constants.MSG_DELIMITER + password;
            sw.WriteLine(msg);
            sw.Flush();
        }

        public void ShowDlProgressBar()
        {
            dl_progress_bar.Show();
        }

        public void SetDlProgressBarValue(int value)
        {
            dl_progress_bar.Value = value;
        }

        public void HideDlProgressBar()
        {
            dl_progress_bar.Hide();
        }

        public string GetUsername()
        {
            return this.username_entry.Text;
        }

        public string GetPassword()
        {
            return this.password_entry.Text;
        }
            

    }
}
