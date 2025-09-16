using Microsoft.UI.Xaml;
using VoiceControlApp.ViewModels;

namespace VoiceControlApp
{
    /// <summary>
    /// An empty window that can be used on its own or navigated to within a Frame.
    /// </summary>
    public sealed partial class MainWindow : Window
    {
        public MainWindowViewModel ViewModel { get; }

        public MainWindow()
        {
            this.InitializeComponent();
            ViewModel = App.GetService<MainWindowViewModel>();
            
            // Set window properties
            Title = "Voice Control for Robot System";
            
            // Set the DataContext for binding
            this.Content.DataContext = ViewModel;
        }
    }
}