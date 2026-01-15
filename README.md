# 圖像距離與圓直徑測量工具 v3.0
# Image Distance & Circle Measurement Tool v3.0

[![GitHub Pages](https://img.shields.io/badge/demo-online-brightgreen)](https://chun-chieh-chang.github.io/ImageDistanceMeasurementTool/)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一個功能強大的圖像測量工具，支持直線距離測量和圓直徑測量，提供桌面版和 Web 版兩種使用方式。

A powerful image measurement tool that supports line distance and circle diameter measurements, available in both desktop and web versions.

## 📋 目錄 | Table of Contents

- [功能特點](#功能特點--features)
- [線上演示](#線上演示--online-demo)
- [安裝說明](#安裝說明--installation)
- [使用方法](#使用方法--usage)
- [技術架構](#技術架構--technical-architecture)
- [開發說明](#開發說明--development)
- [更新日誌](#更新日誌--changelog)
- [作者](#作者--author)
- [授權](#授權--license)

## 🌟 功能特點 | Features

### 核心功能 | Core Features

- **雙模式測量 | Dual Measurement Modes**
  - 📏 直線測量：計算兩點間的直線距離（包括總長度、水平和垂直分量）
  - ⭕ 圓直徑測量：以兩點為直徑繪製圓形並顯示直徑值
  - 📏 Line Measurement: Calculate linear distance between two points (total length, horizontal and vertical components)
  - ⭕ Circle Diameter: Draw a circle using two points as diameter and display the diameter value

- **比例尺設定 | Scale Calibration**
  - 📐 支持使用參考物體設定比例尺
  - 🔢 支持多種單位：mm, cm, m, inch, µm, pixel
  - 📐 Support scale setting using reference objects
  - 🔢 Multiple units supported: mm, cm, m, inch, µm, pixel

- **圖像操作 | Image Operations**
  - 🔍 縮放功能（放大/縮小/重置）
  - 🖱️ 拖動平移圖像
  - 🎨 自定義標記點顏色和大小
  - 📊 實時坐標顯示
  - 🔍 Zoom in/out/reset
  - 🖱️ Pan image by dragging
  - 🎨 Customizable marker color and size
  - 📊 Real-time coordinate display

- **用戶體驗 | User Experience**
  - 🌐 雙語界面（中文/英文）
  - 📝 操作日誌記錄
  - 💾 EXIF 自動旋轉支持
  - 🎯 精確的像素級測量
  - 🌐 Bilingual interface (Chinese/English)
  - 📝 Operation log
  - 💾 EXIF auto-rotation support
  - 🎯 Pixel-level precision

## 🌐 線上演示 | Online Demo

**Web 版本**: [https://chun-chieh-chang.github.io/ImageDistanceMeasurementTool/](https://chun-chieh-chang.github.io/ImageDistanceMeasurementTool/)

Web 版本提供與桌面版相同的核心功能，無需安裝即可直接在瀏覽器中使用。

The web version provides the same core features as the desktop version and can be used directly in a browser without installation.

### Web 版特點 | Web Version Features
- ✅ 無需安裝，即開即用
- ✅ 跨平台支持（Windows, macOS, Linux）
- ✅ 移動設備友好
- ✅ 數據本地處理，保護隱私
- ✅ No installation required
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Mobile-friendly
- ✅ Local data processing for privacy

## 💻 安裝說明 | Installation

### 桌面版 (Python) | Desktop Version (Python)

#### 系統要求 | Requirements
- Python 3.7 或更高版本 | Python 3.7 or higher
- Windows / macOS / Linux

#### 安裝步驟 | Installation Steps

1. **克隆倉庫 | Clone Repository**
```bash
git clone https://github.com/Chun-Chieh-Chang/ImageDistanceMeasurementTool.git
cd ImageDistanceMeasurementTool
```

2. **安裝依賴 | Install Dependencies**
```bash
pip install pillow
```

3. **運行程序 | Run Application**
```bash
python ImageDistanceMeasureTool.py
```

#### 打包為可執行文件 | Build Executable

使用 PyInstaller 打包為獨立可執行文件：

```bash
# 安裝 PyInstaller
pip install pyinstaller

# 打包（參考 打包命令.txt）
pyinstaller --onefile --windowed --icon=app_icon.ico --add-data "author_avatar.png;." ImageDistanceMeasureTool.py
```

### Web 版 | Web Version

Web 版本已部署在 GitHub Pages，無需安裝。如需本地運行：

1. **克隆倉庫 | Clone Repository**
```bash
git clone https://github.com/Chun-Chieh-Chang/ImageDistanceMeasurementTool.git
cd ImageDistanceMeasurementTool/docs
```

2. **啟動本地服務器 | Start Local Server**
```bash
# 使用 Python 內置服務器
python -m http.server 8000

# 或使用 Node.js
npx http-server
```

3. **訪問 | Access**
打開瀏覽器訪問 `http://localhost:8000`

## 📖 使用方法 | Usage

### 快速開始 | Quick Start

#### 1. 設定比例尺（可選）| Set Scale (Optional)

如果需要獲得實際物理單位的測量結果：

1. 加載包含已知尺寸物體（如尺子）的參考圖片到右側面板（圖片 B）
2. 在參考物體上選擇兩個端點
3. 輸入實際物理長度和單位
4. 點擊「設比例尺」按鈕

If you need measurements in actual physical units:

1. Load a reference image with a known-size object (e.g., ruler) to the right panel (Image B)
2. Select two endpoints on the reference object
3. Enter the actual physical length and unit
4. Click "Set Scale" button

#### 2. 加載待測圖片 | Load Target Image

點擊左側面板的「加載待測圖片 (A)」按鈕，選擇要測量的圖片。

Click "Load Image (A)" button on the left panel to select the image you want to measure.

#### 3. 選擇測量模式 | Select Measurement Mode

在底部選擇「直線測量」或「直徑畫圓」模式。

Select "Line Measurement" or "Circle Diameter" mode at the bottom.

#### 4. 進行測量 | Perform Measurement

在圖片 A 上點擊兩個點：
- **直線模式**：兩點定義線段的起點和終點
- **畫圓模式**：兩點定義圓的直徑

Click two points on Image A:
- **Line Mode**: Two points define the start and end of the line segment
- **Circle Mode**: Two points define the diameter of the circle

#### 5. 查看結果 | View Results

測量結果會自動顯示在圖片上和底部信息欄中。

Measurement results will be automatically displayed on the image and in the bottom information bar.

### 進階功能 | Advanced Features

#### 圖像縮放 | Image Zoom
- **放大 +**: 增加圖像顯示大小
- **縮小 -**: 減小圖像顯示大小
- **重置縮放**: 恢復到原始大小

#### 圖像拖動 | Image Pan
按住鼠標中鍵或右鍵拖動圖像。

Press and hold the middle or right mouse button to drag the image.

#### 自定義外觀 | Customize Appearance
- 點擊「點顏色」按鈕選擇標記點顏色
- 調整「點半徑」改變標記點大小

- Click "Pt Color" button to choose marker color
- Adjust "Pt Radius" to change marker size

#### 清除操作 | Clear Operations
- **清除點 (A/B)**: 清除對應面板上的點和圖形
- **重置所有**: 清除所有數據並恢復初始狀態

- **Clear Pts (A/B)**: Clear points and drawings on the corresponding panel
- **Reset All**: Clear all data and restore initial state

## 🏗️ 技術架構 | Technical Architecture

### 桌面版 | Desktop Version

```
ImageDistanceMeasurementTool/
├── ImageDistanceMeasureTool.py    # 主程序文件
├── app_icon.ico                    # 應用圖標
├── author_avatar.png               # 作者頭像
├── ImageDistanceMeasureTool.spec   # PyInstaller 配置
├── 打包命令.txt                    # 打包命令參考
├── crack.jpg                       # 示例圖片 1
├── ruler.jpg                       # 示例圖片 2
└── build/                          # 構建輸出目錄
```

**技術棧 | Tech Stack**:
- **Python 3.7+**: 核心編程語言
- **Tkinter**: GUI 框架
- **PIL/Pillow**: 圖像處理
- **Math**: 數學計算

### Web 版 | Web Version

```
docs/
├── index.html      # 主 HTML 文件
├── script.js       # JavaScript 邏輯
└── style.css       # 樣式文件
```

**技術棧 | Tech Stack**:
- **HTML5 Canvas**: 圖像渲染和繪圖
- **Vanilla JavaScript**: 核心邏輯（無框架依賴）
- **CSS3**: 樣式和佈局

### 核心算法 | Core Algorithms

#### 距離計算 | Distance Calculation
```python
# 歐幾里得距離
distance = √((x₂ - x₁)² + (y₂ - y₁)²)

# 水平分量
horizontal = |x₂ - x₁|

# 垂直分量
vertical = |y₂ - y₁|
```

#### 比例尺轉換 | Scale Conversion
```python
# 比例尺 = 實際距離 / 像素距離
scale = actual_distance / pixel_distance

# 實際測量值 = 像素值 × 比例尺
actual_measurement = pixel_value × scale
```

#### 圓直徑繪製 | Circle Diameter Drawing
```python
# 圓心坐標
center_x = (x₁ + x₂) / 2
center_y = (y₁ + y₂) / 2

# 半徑 = 直徑 / 2
radius = distance / 2
```

## 🛠️ 開發說明 | Development

### 項目結構 | Project Structure

```
ImageDistanceMeasurementTool/
├── .git/                   # Git 版本控制
├── .github/                # GitHub 配置
│   └── workflows/          # GitHub Actions
├── docs/                   # Web 版本源碼
│   ├── index.html
│   ├── script.js
│   └── style.css
├── build/                  # 構建輸出
├── ImageDistanceMeasureTool.py    # 桌面版主程序
├── ImageDistanceMeasureTool.spec  # PyInstaller 配置
├── app_icon.ico            # 應用圖標
├── author_avatar.png       # 作者頭像
├── crack.jpg               # 示例圖片
├── ruler.jpg               # 示例圖片
├── 打包命令.txt            # 打包命令
└── README.md               # 本文件
```

### 開發環境設置 | Development Setup

1. **Fork 本倉庫 | Fork this repository**

2. **創建功能分支 | Create feature branch**
```bash
git checkout -b feature/your-feature-name
```

3. **進行開發 | Make changes**

4. **提交更改 | Commit changes**
```bash
git add .
git commit -m "feat: add your feature description"
```

5. **推送分支 | Push branch**
```bash
git push origin feature/your-feature-name
```

6. **創建 Pull Request | Create Pull Request**

### 代碼規範 | Code Standards

- **Python**: 遵循 PEP 8 規範
- **JavaScript**: 使用 ES6+ 語法
- **提交訊息**: 遵循 Conventional Commits 規範
  - `feat`: 新功能
  - `fix`: 修復 bug
  - `docs`: 文檔更新
  - `style`: 代碼格式調整
  - `refactor`: 重構代碼
  - `test`: 測試相關
  - `chore`: 構建過程或輔助工具的變動

## 📝 更新日誌 | Changelog

### v3.0 (2026-01-15)

#### 新增 | Added
- ✨ Web 版本發布，支持在線使用
- ✨ 修復圖片顯示問題，確保圖片完整顯示
- ✨ Overlay canvas 透明背景，不遮蓋圖片
- ✨ Canvas 和 overlay 尺寸自動同步

#### 修復 | Fixed
- 🐛 修復圖片被裁切的問題
- 🐛 修復 overlay canvas 尺寸不匹配
- 🐛 修復 overlay 灰色背景遮蓋圖片

#### 改進 | Improved
- 🎨 優化 Web 版 UI/UX
- 📱 改善移動設備兼容性
- ⚡ 提升性能和響應速度

### v2.0 (2025-05)

#### 新增 | Added
- ✨ 圓直徑測量模式
- ✨ 雙語界面支持（中文/英文）
- ✨ 自定義標記點顏色和大小
- ✨ 實時坐標顯示

#### 改進 | Improved
- 🎨 UI 界面重新設計
- 📊 增強測量精度
- 🔧 優化圖像處理性能

### v1.0 (2025-04)

#### 新增 | Added
- ✨ 基本直線距離測量功能
- ✨ 比例尺設定功能
- ✨ 圖像縮放和拖動
- ✨ EXIF 自動旋轉支持

## 👨‍💻 作者 | Author

**Wesley Chang**

- GitHub: [@Chun-Chieh-Chang](https://github.com/Chun-Chieh-Chang)
- Email: [您的郵箱]

## 📄 授權 | License

本項目採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 文件

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🙏 致謝 | Acknowledgments

感謝所有為本項目做出貢獻的開發者和用戶。

Thanks to all developers and users who have contributed to this project.

## 📞 聯繫方式 | Contact

如有問題或建議，歡迎：
- 提交 [Issue](https://github.com/Chun-Chieh-Chang/ImageDistanceMeasurementTool/issues)
- 發起 [Pull Request](https://github.com/Chun-Chieh-Chang/ImageDistanceMeasurementTool/pulls)
- 發送郵件至 [您的郵箱]

For questions or suggestions:
- Submit an [Issue](https://github.com/Chun-Chieh-Chang/ImageDistanceMeasurementTool/issues)
- Create a [Pull Request](https://github.com/Chun-Chieh-Chang/ImageDistanceMeasurementTool/pulls)
- Send email to [Your Email]

---

**⭐ 如果這個項目對您有幫助，請給它一個 Star！**

**⭐ If this project helps you, please give it a Star!**
