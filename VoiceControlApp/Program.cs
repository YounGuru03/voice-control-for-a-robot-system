using Microsoft.UI.Xaml;
using System;

namespace VoiceControlApp
{
    /// <summary>
    /// Program entry point for the Voice Control Application
    /// </summary>
    public class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            WinRT.ComWrappersSupport.InitializeComWrappers();
            Application.Start((p) => new App());
        }
    }
}