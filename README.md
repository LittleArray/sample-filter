# 图片样本筛选器

一个基于 Python Tkinter 的图片查看与筛选工具。可以快速浏览 `input` 文件夹中的图片，将选中的图片剪切到 `output` 文件夹，并支持撤销操作。

## 功能特性

- 预览 `./input` 目录下的常见格式图片（jpg, png, gif, bmp 等）
- 按 **Enter** 键将当前图片剪切到 `./output` 文件夹
- 按 **Z** 键撤销上一次剪切操作（将图片移回 `input`）
- 按 **←** / **→** 方向键切换上一张/下一张图片
- 界面底部提供完整操作提示
- 自动记录操作历史，支持连续撤销

## 环境要求

- Python 3.6 或更高版本
- 依赖库：`Pillow`（Python Imaging Library 分支）

## 快速开始

### 1. 克隆或下载项目

```bash
git clone <your-repo-url>
cd image-screener