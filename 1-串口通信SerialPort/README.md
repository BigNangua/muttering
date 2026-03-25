## 一、串口通讯简介

* 串口通讯（Serial Communication）是按位顺序发送数据的通信方式。
* 常见标准：

  * **RS-232**：电脑经典串口
  * **RS-485**：工业现场串口
  * **TTL Serial**：单片机常用

---

## 二、串口核心参数

1. **波特率（Baud Rate）**：传输速度，如 9600、115200
2. **数据位（Data Bits）**：一般为 8
3. **停止位（Stop Bits）**：一般为 1
4. **校验位（Parity）**：None / Even / Odd

**常见配置：** `9600, 8, N, 1`

---

## 三、模拟串口环境

### 推荐工具

* **Virtual Serial Port Driver（虚拟串口）**
  * https://virtualserialportdriver.cn/
* llcom（串口调试工具）
  * https://github.com/chenxuuu/llcom


### 实验1：创建虚拟串口对

* 创建 COM3 ↔ COM4
* 目标：COM3 发数据 → COM4 收到

### 实验2：串口通信演示

1. 打开两个串口工具窗口：

   * 窗口A：COM3
   * 窗口B：COM4
2. 配置参数：`9600, 8, N, 1`
3. 在 A 输入 `hello` → B 能收到 `hello`

   ![image-20260325162843670](https://raw.githubusercontent.com/BigNangua/muttering/refs/heads/main/img/image-20260325162843670.png)

---

## 四、理解串口数据

* 串口传输的是**字节**，字符串需转换成字节流。
* 示例：

  ```
  字符: A
  ASCII: 65
  HEX: 0x41
  ```
* 发送 "ABC" → 0x41 0x42 0x43

---

## 五、协议模拟

* 工业通讯通常用协议，而不是直接发字符串：

  * **Modbus RTU**：工业最常用协议
* 示例：

  * 发送：`01 03 00 00 00 01 84 0A`（读取设备1寄存器）
  * 接收：`01 03 02 00 64 B9 84`（寄存器值 = 100）

---

## 六、C# 串口操作示例

### 发送数据

```csharp
using System;
using System.IO.Ports;

class SerialSend
{
    static void Main()
    {
        SerialPort serialPort = new SerialPort("COM3", 9600, Parity.None, 8, StopBits.One);

        serialPort.Open();

        string message = "hello";
        serialPort.Write(message); // 发送字符串
        Console.WriteLine($"已发送: {message}");

        serialPort.Close();
    }
}
```

### 接收数据

```csharp
using System;
using System.IO.Ports;

class SerialReceive
{
    static void Main()
    {
        SerialPort serialPort = new SerialPort("COM4", 9600, Parity.None, 8, StopBits.One);

        serialPort.Open();

        byte[] buffer = new byte[5];
        int bytesRead = serialPort.Read(buffer, 0, buffer.Length);
        string received = System.Text.Encoding.ASCII.GetString(buffer, 0, bytesRead);

        Console.WriteLine($"收到数据: {received}");

        serialPort.Close();
    }
}
```

---

## 七、学习路径建议

1. 搭建虚拟串口 → 跑通 hello
2. 用 HEX 发送数据 → 理解字节
3. 模拟 Modbus 收发
4. 用 C# 写“小主站”程序



## 注意事项（波特率）：

​	

虚拟串口：可以随便设置不同波特率练习 **程序逻辑**、**HEX 解析**

真实串口：**波特率、停止位、校验位必须完全一致**，否则通信失败

![image-20260325171922279](https://raw.githubusercontent.com/BigNangua/muttering/refs/heads/main/img/image-20260325171922279.png)



### C# 示例：

**1、虚拟串口不同波特率也能正常通信**

**2、如果是模拟真实串口不一致波特率，会看到错误**

SerialDemo.cs

```c#
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

```

Program.cs

```c#
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

```

![image-20260325174855349](https://raw.githubusercontent.com/BigNangua/muttering/refs/heads/main/img/image-20260325174855349.png)



#### RS-232 和 RS-485

| 特性           | RS-232                                 | RS-485                              |
| -------------- | -------------------------------------- | ----------------------------------- |
| **传输方式**   | 单端（相对于地 GND）                   | 差分（A、B 两条线信号相反）         |
| **接口电平**   | ±12V（逻辑1=-3~ -15V，逻辑0=+3~ +15V） | 差分 5V 或 ±2V（A-B 电压差表示1/0） |
| **线缆长度**   | 短（一般≤15米）                        | 长（可达1200米）                    |
| **抗干扰能力** | 较弱                                   | 强（差分信号抗干扰）                |
| **最大节点数** | 1对1（点对点）                         | 多点（可挂32个节点，RS-485标准）    |
| **标准连接**   | DB9 或 DB25                            | 通常是两线或四线（A/B 差分对）      |



##### 通信拓扑差异

- RS-232
  - 点对点：**一个发送端，一个接收端**
  - 适合短距离、低速、单机调试
- RS-485
  - 总线型：**一条总线，多节点**
  - 可以多个设备收发数据（半双工或全双工）
  - 广泛用于工业现场（PLC、传感器、HMI）



##### 电气和传输特性

RS-232

- 单端信号，相对于地参考
- 容易受地线干扰影响
- 速度一般 ≤115.2 kbps，距离短

RS-485

- 差分信号，A/B 电压差表示逻辑
- 抗干扰能力强
- 半双工总线模式常用
- 高速长距离传输能力（10 Mbps @ 10m，100 kbps @ 1200m）

##### 应用场景

| 接口   | 常见场景                                                 |
| ------ | -------------------------------------------------------- |
| RS-232 | 调试串口、PC 与仪器点对点连接、小型设备                  |
| RS-485 | 工业控制现场总线（Modbus RTU）、PLC 通信、远距离数据采集 |



**RS-232 → 点对点、短距离、低抗干扰、单机调试**

**RS-485 → 多节点、长距离、高抗干扰、工业现场总线**

![6ba7b810-9dad-11d1-80b4-00c04fd430c8](https://raw.githubusercontent.com/BigNangua/muttering/refs/heads/main/img/6ba7b810-9dad-11d1-80b4-00c04fd430c8.png)
