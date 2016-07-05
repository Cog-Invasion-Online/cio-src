using System;

/// <summary>
/// Summary description for Constants
/// </summary>
public static class Constants
{
    public const string LOGIN_SERVER_DEV = "gameserver-dev.coginvasion.com";
    public const string LOGIN_SERVER = "gameserver.coginvasion.com";
    public const int LOGIN_PORT = 7033;

    public const int CL_SERVER_INFO = 1;
    public const int SV_SERVER_INFO = 2;
    public const int CL_REQ_PLAY = 3;
    public const int CL_REQ_BASE_LINK = 4;
    public const int SV_BASE_LINK = 5;
    public const int CL_REQ_CREATE_ACC = 6;
    public const int SV_CREATE_ACC_RESP = 7;
    public const int SV_PLAY_RESP = 8;
    public const int SV_MSG = 9;

    public const string LAUNCHER_VER = "1.1";

    public const string MSG_DELIMITER = ";";

    public const int STATE_STARTUP = 0;
    public const int STATE_VALIDATING = 1;
    public const int STATE_LOGIN_MENU = 2;
    public const int STATE_ACC_CREATE_MENU = 3;
    public const int STATE_ACC_SUBMITTING = 4;
    public const int STATE_LOGGING_IN = 5;
    public const int STATE_GET_BASE_LINK = 6;
    public const int STATE_UPDATE_FILES = 7;
    public const int STATE_GEN_DL_LIST = 8;

    public const string CONTACT_LINK = "http://coginvasion.com/contact-us.html";

    public const string STATUS_CONNECTING = "Connecting...";
    public const string STATUS_VALIDATING = "Validating...";
    public const string STATUS_FETCHING = "Fetching download list...";
    public const string STATUS_SUBMIT = "Submitting...";
    public const string STATUS_LOGGING = "Logging in...";
    public const string STATUS_STARTING = "Starting game...";
    public const string STATUS_FILE_DATA = "File {0} of {1}... ({2})";
    public const string UPDATING_FILES = "Updating files...";

    public const bool IS_DEV = true;
    public const string DEV_INSTALLER = "http://download.coginvasion.com/installers/setup-dev.exe";
    public const string DL_PAGE = "http://coginvasion.com/play";
}
