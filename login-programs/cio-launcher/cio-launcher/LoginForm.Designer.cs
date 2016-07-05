namespace cio_launcher
{
    partial class LoginForm
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(LoginForm));
            this.bg_image = new System.Windows.Forms.PictureBox();
            this.username_lbl = new System.Windows.Forms.Label();
            this.password_lbl = new System.Windows.Forms.Label();
            this.username_entry = new System.Windows.Forms.TextBox();
            this.password_entry = new System.Windows.Forms.TextBox();
            this.play_btn = new System.Windows.Forms.Button();
            this.login_lbl = new System.Windows.Forms.Label();
            this.contact_btn = new System.Windows.Forms.Button();
            this.create_acc_btn = new System.Windows.Forms.Button();
            this.back_btn = new System.Windows.Forms.Button();
            this.status_lbl = new System.Windows.Forms.Label();
            this.dl_progress_bar = new System.Windows.Forms.ProgressBar();
            ((System.ComponentModel.ISupportInitialize)(this.bg_image)).BeginInit();
            this.SuspendLayout();
            // 
            // bg_image
            // 
            this.bg_image.Image = ((System.Drawing.Image)(resources.GetObject("bg_image.Image")));
            this.bg_image.Location = new System.Drawing.Point(-27, -26);
            this.bg_image.Name = "bg_image";
            this.bg_image.Size = new System.Drawing.Size(640, 480);
            this.bg_image.TabIndex = 0;
            this.bg_image.TabStop = false;
            // 
            // username_lbl
            // 
            this.username_lbl.AutoSize = true;
            this.username_lbl.BackColor = System.Drawing.Color.Transparent;
            this.username_lbl.Font = new System.Drawing.Font("Microsoft Sans Serif", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.username_lbl.ForeColor = System.Drawing.Color.White;
            this.username_lbl.Location = new System.Drawing.Point(157, 190);
            this.username_lbl.Name = "username_lbl";
            this.username_lbl.Size = new System.Drawing.Size(68, 15);
            this.username_lbl.TabIndex = 1;
            this.username_lbl.Text = "Username:";
            // 
            // password_lbl
            // 
            this.password_lbl.AutoSize = true;
            this.password_lbl.BackColor = System.Drawing.Color.Transparent;
            this.password_lbl.Font = new System.Drawing.Font("Microsoft Sans Serif", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.password_lbl.ForeColor = System.Drawing.Color.White;
            this.password_lbl.Location = new System.Drawing.Point(161, 222);
            this.password_lbl.Name = "password_lbl";
            this.password_lbl.Size = new System.Drawing.Size(64, 15);
            this.password_lbl.TabIndex = 2;
            this.password_lbl.Text = "Password:";
            // 
            // username_entry
            // 
            this.username_entry.Location = new System.Drawing.Point(231, 189);
            this.username_entry.Name = "username_entry";
            this.username_entry.Size = new System.Drawing.Size(131, 20);
            this.username_entry.TabIndex = 3;
            this.username_entry.KeyUp += new System.Windows.Forms.KeyEventHandler(this.username_entry_KeyUp);
            // 
            // password_entry
            // 
            this.password_entry.Location = new System.Drawing.Point(231, 221);
            this.password_entry.Name = "password_entry";
            this.password_entry.PasswordChar = '*';
            this.password_entry.Size = new System.Drawing.Size(131, 20);
            this.password_entry.TabIndex = 4;
            this.password_entry.KeyUp += new System.Windows.Forms.KeyEventHandler(this.password_entry_KeyUp);
            // 
            // play_btn
            // 
            this.play_btn.Location = new System.Drawing.Point(368, 204);
            this.play_btn.Name = "play_btn";
            this.play_btn.Size = new System.Drawing.Size(51, 23);
            this.play_btn.TabIndex = 5;
            this.play_btn.Text = "Play";
            this.play_btn.UseVisualStyleBackColor = true;
            this.play_btn.Click += new System.EventHandler(this.play_btn_Click);
            // 
            // login_lbl
            // 
            this.login_lbl.BackColor = System.Drawing.Color.Transparent;
            this.login_lbl.Font = new System.Drawing.Font("Microsoft Sans Serif", 11F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.login_lbl.ForeColor = System.Drawing.Color.White;
            this.login_lbl.Location = new System.Drawing.Point(0, 160);
            this.login_lbl.Name = "login_lbl";
            this.login_lbl.Size = new System.Drawing.Size(582, 18);
            this.login_lbl.TabIndex = 6;
            this.login_lbl.Text = "Log-In";
            this.login_lbl.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // contact_btn
            // 
            this.contact_btn.FlatStyle = System.Windows.Forms.FlatStyle.System;
            this.contact_btn.Location = new System.Drawing.Point(216, 401);
            this.contact_btn.Name = "contact_btn";
            this.contact_btn.Size = new System.Drawing.Size(146, 23);
            this.contact_btn.TabIndex = 7;
            this.contact_btn.Text = "Contact Us/Report A Bug";
            this.contact_btn.UseVisualStyleBackColor = true;
            this.contact_btn.Click += new System.EventHandler(this.contact_btn_Click);
            // 
            // create_acc_btn
            // 
            this.create_acc_btn.Location = new System.Drawing.Point(245, 260);
            this.create_acc_btn.Name = "create_acc_btn";
            this.create_acc_btn.Size = new System.Drawing.Size(91, 23);
            this.create_acc_btn.TabIndex = 8;
            this.create_acc_btn.Text = "Create Account";
            this.create_acc_btn.UseVisualStyleBackColor = true;
            this.create_acc_btn.Click += new System.EventHandler(this.create_acc_btn_Click);
            // 
            // back_btn
            // 
            this.back_btn.Location = new System.Drawing.Point(170, 260);
            this.back_btn.Name = "back_btn";
            this.back_btn.Size = new System.Drawing.Size(29, 23);
            this.back_btn.TabIndex = 9;
            this.back_btn.Text = "<<";
            this.back_btn.UseVisualStyleBackColor = true;
            this.back_btn.Visible = false;
            this.back_btn.Click += new System.EventHandler(this.back_btn_Click);
            // 
            // status_lbl
            // 
            this.status_lbl.BackColor = System.Drawing.Color.Transparent;
            this.status_lbl.Font = new System.Drawing.Font("Microsoft Sans Serif", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.status_lbl.ForeColor = System.Drawing.Color.White;
            this.status_lbl.Location = new System.Drawing.Point(0, 205);
            this.status_lbl.Name = "status_lbl";
            this.status_lbl.Size = new System.Drawing.Size(582, 18);
            this.status_lbl.TabIndex = 10;
            this.status_lbl.Text = "Connecting...";
            this.status_lbl.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            this.status_lbl.Visible = false;
            // 
            // dl_progress_bar
            // 
            this.dl_progress_bar.Location = new System.Drawing.Point(227, 226);
            this.dl_progress_bar.Name = "dl_progress_bar";
            this.dl_progress_bar.Size = new System.Drawing.Size(131, 20);
            this.dl_progress_bar.TabIndex = 11;
            this.dl_progress_bar.Visible = false;
            // 
            // LoginForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(581, 436);
            this.Controls.Add(this.dl_progress_bar);
            this.Controls.Add(this.status_lbl);
            this.Controls.Add(this.back_btn);
            this.Controls.Add(this.create_acc_btn);
            this.Controls.Add(this.contact_btn);
            this.Controls.Add(this.login_lbl);
            this.Controls.Add(this.play_btn);
            this.Controls.Add(this.password_entry);
            this.Controls.Add(this.username_entry);
            this.Controls.Add(this.password_lbl);
            this.Controls.Add(this.username_lbl);
            this.Controls.Add(this.bg_image);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.MaximizeBox = false;
            this.Name = "LoginForm";
            this.Text = "Cog Invasion Online Launcher";
            ((System.ComponentModel.ISupportInitialize)(this.bg_image)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.PictureBox bg_image;
        private System.Windows.Forms.Label username_lbl;
        private System.Windows.Forms.Label password_lbl;
        private System.Windows.Forms.TextBox username_entry;
        private System.Windows.Forms.TextBox password_entry;
        private System.Windows.Forms.Button play_btn;
        private System.Windows.Forms.Label login_lbl;
        private System.Windows.Forms.Button contact_btn;
        private System.Windows.Forms.Button create_acc_btn;
        private System.Windows.Forms.Button back_btn;
        private System.Windows.Forms.Label status_lbl;
        private System.Windows.Forms.ProgressBar dl_progress_bar;
    }
}