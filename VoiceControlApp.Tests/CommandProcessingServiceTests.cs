using Microsoft.VisualStudio.TestTools.UnitTesting;
using VoiceControlApp.Services;
using Microsoft.Extensions.Logging;
using System.Threading.Tasks;

namespace VoiceControlApp.Tests
{
    [TestClass]
    public class CommandProcessingServiceTests
    {
        private CommandProcessingService _commandService;

        [TestInitialize]
        public void Setup()
        {
            var logger = LoggerFactory.Create(builder => builder.AddConsole())
                .CreateLogger<CommandProcessingService>();
            _commandService = new CommandProcessingService(logger);
        }

        [TestMethod]
        public async Task ProcessTextAsync_OpenMain_ReturnsOpenMain()
        {
            // Arrange
            var input = "open main";

            // Act
            var result = await _commandService.ProcessTextAsync(input);

            // Assert
            Assert.AreEqual("open main", result);
        }

        [TestMethod]
        public async Task ProcessTextAsync_OpenRobot_ReturnsOpenRobot()
        {
            // Arrange
            var input = "open robot";

            // Act
            var result = await _commandService.ProcessTextAsync(input);

            // Assert
            Assert.AreEqual("open robot", result);
        }

        [TestMethod]
        public async Task ProcessTextAsync_Alarm_ReturnsAlarm()
        {
            // Arrange
            var input = "alarm";

            // Act
            var result = await _commandService.ProcessTextAsync(input);

            // Assert
            Assert.AreEqual("alarm", result);
        }

        [TestMethod]
        public async Task ProcessTextAsync_OpenCamera1_ReturnsOpenCamera1()
        {
            // Arrange
            var input = "open camera 1";

            // Act
            var result = await _commandService.ProcessTextAsync(input);

            // Assert
            Assert.AreEqual("open camera 1", result);
        }

        [TestMethod]
        public async Task ProcessTextAsync_CloseCamera2_ReturnsCloseCamera2()
        {
            // Arrange
            var input = "close camera 2";

            // Act
            var result = await _commandService.ProcessTextAsync(input);

            // Assert
            Assert.AreEqual("close camera 2", result);
        }

        [TestMethod]
        public async Task ProcessTextAsync_TemplateA_ReturnsTemplateA()
        {
            // Arrange
            var input = "template A";

            // Act
            var result = await _commandService.ProcessTextAsync(input);

            // Assert
            Assert.AreEqual("template A", result);
        }

        [TestMethod]
        public async Task ProcessTextAsync_Template7_ReturnsTemplate7()
        {
            // Arrange
            var input = "template 7";

            // Act
            var result = await _commandService.ProcessTextAsync(input);

            // Assert
            Assert.AreEqual("template 7", result);
        }

        [TestMethod]
        public async Task ProcessTextAsync_UnknownCommand_ReturnsNone()
        {
            // Arrange
            var input = "hello world";

            // Act
            var result = await _commandService.ProcessTextAsync(input);

            // Assert
            Assert.AreEqual("None", result);
        }

        [TestMethod]
        public async Task ProcessTextAsync_NaturalLanguage_ExtractsCommand()
        {
            // Arrange
            var input = "um, can you please open main application";

            // Act
            var result = await _commandService.ProcessTextAsync(input);

            // Assert
            Assert.AreEqual("open main", result);
        }

        [TestMethod]
        public void GetSupportedCommands_ReturnsAllCommands()
        {
            // Act
            var commands = _commandService.GetSupportedCommands();

            // Assert
            Assert.AreEqual(30, commands.Length);
            Assert.IsTrue(Array.Exists(commands, c => c == "open main"));
            Assert.IsTrue(Array.Exists(commands, c => c == "alarm"));
            Assert.IsTrue(Array.Exists(commands, c => c == "template A"));
            Assert.IsTrue(Array.Exists(commands, c => c == "template 10"));
        }

        [TestMethod]
        public void IsEmergencyCommand_Alarm_ReturnsTrue()
        {
            // Act & Assert
            Assert.IsTrue(_commandService.IsEmergencyCommand("alarm"));
        }

        [TestMethod]
        public void IsEmergencyCommand_OpenMain_ReturnsFalse()
        {
            // Act & Assert
            Assert.IsFalse(_commandService.IsEmergencyCommand("open main"));
        }
    }
}