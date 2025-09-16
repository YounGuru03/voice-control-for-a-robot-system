using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.UI.Xaml;
using System;
using VoiceControlApp.Services;
using VoiceControlApp.ViewModels;

namespace VoiceControlApp
{
    /// <summary>
    /// Provides application-specific behavior to supplement the default Application class.
    /// </summary>
    public partial class App : Application
    {
        private IHost _host;
        private Window _window;

        /// <summary>
        /// Initializes the singleton application object.  This is the first line of authored code
        /// executed, and as such is the logical equivalent of main() or WinMain().
        /// </summary>
        public App()
        {
            this.InitializeComponent();
            
            // Configure services
            _host = Host.CreateDefaultBuilder()
                .UseContentRoot(AppContext.BaseDirectory)
                .ConfigureServices((context, services) =>
                {
                    // Core services
                    services.AddSingleton<IAudioService, AudioService>();
                    services.AddSingleton<IVoiceRecognitionService, VoiceRecognitionService>();
                    services.AddSingleton<ICommandProcessingService, CommandProcessingService>();
                    services.AddSingleton<IFileOutputService, FileOutputService>();
                    
                    // ViewModels
                    services.AddTransient<MainWindowViewModel>();
                })
                .ConfigureLogging((context, logging) =>
                {
                    logging.ClearProviders();
                    logging.AddConsole();
                    logging.SetMinimumLevel(LogLevel.Information);
                })
                .Build();
        }

        /// <summary>
        /// Invoked when the application is launched normally by the end user.
        /// </summary>
        protected override void OnLaunched(LaunchActivatedEventArgs args)
        {
            _window = new MainWindow();
            
            // Initialize services
            var fileOutputService = _host.Services.GetRequiredService<IFileOutputService>();
            fileOutputService.ClearOutputFile(); // Clear text.txt at startup as required
            
            _window.Activate();
        }

        /// <summary>
        /// Get a service from the DI container
        /// </summary>
        public static T GetService<T>() where T : class
        {
            return ((App)Current)._host.Services.GetRequiredService<T>();
        }

        /// <summary>
        /// Clean up resources when app is closing
        /// </summary>
        protected override void OnClosing()
        {
            _host?.Dispose();
            base.OnClosing();
        }
    }
}