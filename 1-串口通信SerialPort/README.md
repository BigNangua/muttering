## 一、串口通讯简介

* 串口通讯（Serial Communication）是按位顺序发送数据的通信方式。
* 常见标准：

  * **RS-232**：电脑经典串口
  * **RS-485**：工业现场串口
  * **TTL Serial**：单片机常用

> 简单理解：串口 = 一根线按顺序发字节

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

---

## 八、学习提醒

* 光会用串口工具没用，要会：

  * 解析协议
  * 写程序通讯
  * 对接 PLC / MES
