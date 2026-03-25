using System.IO.Ports;
using System.Text;

namespace VirtualModbusDemo
{
    public class SerialDemo
    {
        private SerialPort masterPort;
        private SerialPort slavePort;
        private bool slaveRunning = false;

        // 构造函数：使用已有虚拟串口对象
        public SerialDemo(SerialPort masterPort, SerialPort slavePort)
        {
            this.masterPort = masterPort;
            this.slavePort = slavePort;
        }

        // 原始运行逻辑
        public void Run()
        {
            OpenPorts();

            StartSlaveThread();

            // 主站发送数据
            byte[] testData = Encoding.ASCII.GetBytes("Hello Virtual Serial!");
            masterPort.Write(testData, 0, testData.Length);
            Thread.Sleep(200);

            ReadMaster();

            StopSlaveThread();
        }

        // 增加：波特率不一致模拟错误
        public void RunWithErrorSimulation(int masterBaud, int slaveBaud)
        {
            OpenPorts();

            StartSlaveThread();

            byte[] testData = Encoding.ASCII.GetBytes("Hello Virtual Serial!");
            masterPort.Write(testData, 0, testData.Length);
            Thread.Sleep(200);

            byte[] recv = ReadMasterBytesWithError(masterBaud, slaveBaud);
            Console.WriteLine($"模拟接收数据（主:{masterBaud} 波特率， 从:{slaveBaud} 波特率）: " + Encoding.ASCII.GetString(recv));
            Console.WriteLine("接收端 HEX: " + BitConverter.ToString(recv));

            StopSlaveThread();
        }

        // ------------------ 内部方法 ------------------
        private void OpenPorts()
        {
            if (!masterPort.IsOpen) masterPort.Open();
            if (!slavePort.IsOpen) slavePort.Open();
        }

        private void StartSlaveThread()
        {
            slaveRunning = true;
            Thread slaveThread = new Thread(() =>
            {
                while (slaveRunning)
                {
                    try
                    {
                        if (slavePort.BytesToRead > 0)
                        {
                            byte[] buffer = new byte[slavePort.BytesToRead];
                            int read = slavePort.Read(buffer, 0, buffer.Length);
                            slavePort.Write(buffer, 0, read);
                        }
                    }
                    catch { }
                    Thread.Sleep(10);
                }
            });
            slaveThread.IsBackground = true;
            slaveThread.Start();
        }

        private void StopSlaveThread()
        {
            slaveRunning = false;
            Thread.Sleep(50); // 等待线程安全退出
            if (masterPort.IsOpen) masterPort.Close();
            if (slavePort.IsOpen) slavePort.Close();
        }

        private void ReadMaster()
        {
            if (masterPort.BytesToRead > 0)
            {
                byte[] recv = new byte[masterPort.BytesToRead];
                masterPort.Read(recv, 0, recv.Length);
                Console.WriteLine("虚拟串口接收: " + Encoding.ASCII.GetString(recv));
                Console.WriteLine("接收 HEX: " + BitConverter.ToString(recv));
            }
        }

        private byte[] ReadMasterBytesWithError(int masterBaud, int slaveBaud)
        {
            byte[] recv = new byte[masterPort.BytesToRead];
            masterPort.Read(recv, 0, recv.Length);

            if (masterBaud != slaveBaud)
            {
                // 模拟波特率不一致造成的错误
                Random rnd = new Random();
                for (int i = 0; i < recv.Length; i++)
                {
                    if (rnd.NextDouble() < 0.3) // 30% 字节出错
                        recv[i] = (byte)rnd.Next(0, 256);
                }
            }

            return recv;
        }
    }
}
