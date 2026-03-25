using System.IO.Ports;

namespace VirtualModbusDemo
{
    public class Program
    {
        static void Main(string[] args)
        {
            // 假设虚拟串口已创建：COM3 ↔ COM4
            SerialPort master = new SerialPort("COM3", 9600, Parity.None, 8, StopBits.One);
            SerialPort slave = new SerialPort("COM4", 9600, Parity.None, 8, StopBits.One);

            SerialDemo demo = new SerialDemo(master, slave);

            Console.WriteLine("=== 普通运行 ===");
            demo.Run();

            Console.WriteLine("\n=== 模拟波特率不一致错误 ===");
            demo.RunWithErrorSimulation(masterBaud: 115200, slaveBaud: 9600);

            Console.WriteLine("\n按任意键退出...");
            Console.ReadKey();
        }
    }
}
