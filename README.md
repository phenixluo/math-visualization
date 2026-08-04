# 可视化学习网站

用 AI 写的辅助小孩理解和学习的网页，涵盖数学可视化和英语自然拼读，有兴趣的也可以帮忙完善修改。

## 项目概述

- **预览地址**: https://www.math-v.cc.cd/

这是一个跨学科可视化学习网站，包含以下功能模块：

### 数学图形化

- **函数图像** - 可视化展示各种数学函数
- **几何建模** - 交互式几何图形绘制（点、线、面、立体）
- **3D 图形** - 三维几何图形展示（正六面体、正八面体、球体）
- **公式推导** - 乘法分配律演示（篮子+鸡鸭比喻，支持直接乘法/展开/合并三种模式）
- **方程图形化** - 天平方程游戏，通过天平理解等式两边相等的关系

### 英语音节学习

- **音节拆分** - 基于自然拼读规则引擎的任意单词音节拆分，支持音节内字母段（grapheme）切分，标注元音/辅音段类型、双辅音关联、magic e 等规则
- **音节类型** - 6 种基本音节类型（闭音节/开音节/相对开音节/R控制/双元音/辅音+le）教学，支持输入任意单词实时判型
- **音节发音** - 自然拼读发音参考表，按发音分组（如 a_e/ai/ay 同属 /eɪ/ 组），支持 Web Speech API 点击听发音

## 技术栈

| 技术 | 版本 |
|------|------|
| Vue | 3.4+ |
| Vite | 5.2+ |
| Tailwind CSS | 3.4+ |
| mathjs | 12.4+ |
| d3 | 7.8+ |
| three.js | 0.162+ |
| katex | 0.16+ |

## 环境要求

- Node.js >= 18.0.0
- npm >= 9.0.0
- Git >= 2.0.0

## 本地开发

### 1. 克隆仓库

```bash
git clone git@github.com:phenixluo/math-visualization.git
cd math-visualization
```

### 2. 安装依赖

```bash
npm install
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173 查看效果。

### 4. 构建生产版本

```bash
npm run build
```

构建产物输出到 `dist/` 目录。

### 5. 预览生产版本

```bash
npm run preview
```

## 项目结构

```
math-visualization/
├── src/
│   ├── components/          # Vue 组件
│   │   ├── BalanceGame.vue  # 方程图形化（天平方程游戏）
│   │   ├── FunctionPlot.vue # 函数图像
│   │   ├── GeometryModeler.vue # 几何建模
│   │   ├── Geometry3D.vue   # 3D 图形
│   │   └── FormulaDemo.vue  # 公式推导（乘法分配律）
│   ├── views/               # 视图组件
│   │   ├── MathView.vue     # 数学图形化视图（含5个子tab）
│   │   └── EnglishView.vue  # 英语音节学习视图（含3个子tab）
│   ├── App.vue              # 根组件（顶层导航：数学/英语切换）
│   └── main.js              # 入口文件
├── dist/                    # 构建产物（自动生成）
├── index.html               # HTML 模板
├── package.json             # 项目配置
├── vite.config.js           # Vite 配置
└── tailwind.config.js       # Tailwind CSS 配置
```

## 配置文件说明

### vite.config.js

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  }
})
```

### tailwind.config.js

```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        }
      }
    }
  },
  plugins: []
}
```

## 常见问题

### Q1: 构建时报错 `Error: Cannot find module`

**解决方案**：重新安装依赖

```bash
rm -rf node_modules package-lock.json
npm install
```

### Q2: 页面样式丢失

**解决方案**：检查资源路径是否正确引用，确保 `dist/` 目录结构完整。

### Q3: 部署后页面空白

**解决方案**：打开浏览器开发者工具，查看 Console 是否有错误，通常是 JavaScript 运行时错误或资源加载失败。

### Q4: 英语音节拆分不准确

**说明**：拆分基于自然拼读规则引擎，覆盖 95%+ 常见词。少数例外词（如 have、busy、area 等）规则判型可能有偏差，不维护例外词库。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
