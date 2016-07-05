using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net.NetworkInformation;

namespace cio_launcher
{
    static class Globals
    {
        public static int current_state = Constants.STATE_STARTUP;
        public static string dl_base_link = "";

        public static Launcher launcher;

        public static string GetMacAddress()
        {
            NetworkInterface[] nics = NetworkInterface.GetAllNetworkInterfaces();
            string sMacAddress = string.Empty;
            foreach (NetworkInterface nic in nics)
            {
                if (sMacAddress == string.Empty)
                {
                    sMacAddress = nic.GetPhysicalAddress().ToString();
                }
            }
            Console.WriteLine(sMacAddress);
            return sMacAddress;
        }
    }
}
