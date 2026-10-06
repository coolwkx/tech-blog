---
article_id: kp-29a3817b8b0b9ed7
learning_kind: article
learning_category: 04-dl
learning_direction: foundations
learning_topic: topic-c08205495b15
learning_sourceId: c08205495b15
learning_order: 12
learning_objective: 理解并验证：-CNN卷积神经网络：可运行示例
---

# -CNN卷积神经网络：可运行示例

> **学习目标**：能够解释「-CNN卷积神经网络：可运行示例」的机制或步骤，并用本节材料验证理解。
>
> **前置知识**：全连接前馈网络与反向传播（第 4 章）、梯度下降与 ReLU、张量的维度概念（NCHW）、numpy/PyTorch 基础张量操作。
>
> **所属主题**：-CNN卷积神经网络 · 可运行示例

## 本次只学这一点

下面用 PyTorch 搭一个小 CNN，处理一个 batch 的 $32\times32$ 彩色图，并**在代码里按公式手工校验每一步的输出尺寸与参数量**。

```python
import torch
import torch.nn as nn

torch.manual_seed(0)


def conv_out(i, k, s=1, p=0, d=1):
    """卷积/汇聚层输出尺寸公式: o = floor((i + 2p - d*(k-1) - 1) / s) + 1
    当 d == 1 时等价于教材的 (i + 2p - k)//s + 1"""
    return (i + 2 * p - d * (k - 1) - 1) // s + 1


class SmallCNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        # 卷积层: 3 -> 16 通道, 3x3 核, stride=1, padding=1 => 输出空间尺寸不变
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1)
        # 汇聚层: 2x2 不重叠最大汇聚, 空间尺寸减半
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        # 第二个卷积块: 16 -> 32 通道, stride=2 的卷积自带下采样(替代一次汇聚)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1)
        self.act = nn.ReLU(inplace=False)
        # 32x32 -> pool -> 16x16 -> conv2(s=2) -> 8x8, 通道 32
        self.fc = nn.Linear(32 * 8 * 8, num_classes)

        def forward(self, x, verbose=False):
            if verbose:
                print("input ", tuple(x.shape))
                x = self.act(self.conv1(x))
                if verbose:
                    print("after conv1 ", tuple(x.shape))
                    x = self.pool(x)
                    if verbose:
                        print("after pool ", tuple(x.shape))
                        x = self.act(self.conv2(x))
                        if verbose:
                            print("after conv2(s=2)", tuple(x.shape))
                            x = x.flatten(1) # (N, C, H, W) -> (N, C*H*W)
                            if verbose:
                                print("flatten ", tuple(x.shape))
                                return self.fc(x)


                            # ---------- 1) 按公式手工校验输出尺寸 ----------
                            i, k, s, p = 32, 3, 1, 1
                            print("[check] conv1: i=%d k=%d s=%d p=%d -> %d (期望 32)" % (i, k, s, p, conv_out(i, k, s, p)))
                            assert conv_out(32, 3, 1, 1) == 32
                            assert conv_out(32, 2, 2, 0) == 16 # MaxPool2d(2, 2): 32 -> 16
                            assert conv_out(16, 3, 2, 1) == 8 # conv2: 16 -> 8

                            # ---------- 2) 前向一个 batch, 用真实张量尺寸对照公式 ----------
                            model = SmallCNN()
                            x = torch.randn(4, 3, 32, 32) # NCHW: batch=4, 3 通道, 32x32
                            y = model(x, verbose=True)
                            print("logits ", tuple(y.shape))
                            assert y.shape == (4, 10)

                            # ---------- 3) 打印 conv.weight.shape, 说明参数量 ----------
                            for name, layer in [("conv1", model.conv1), ("conv2", model.conv2)]:
                                w, b = layer.weight, layer.bias
                                C_out, C_in, kh, kw = w.shape
                                manual = kh * kw * C_in * C_out + C_out # K*K*D*D' + D'
                                print(f"{name}: weight.shape={tuple(w.shape)}, bias.shape={tuple(b.shape)}, "
                                f"参数量={w.numel() + b.numel()} (公式 K*K*D*D'+D' = {manual})")
                                assert w.numel() + b.numel() == manual

                                # conv1: 3*3*3*16 + 16 = 448 ; conv2: 3*3*16*32 + 32 = 4640
                                print("模型可训练参数总量:", sum(p.numel() for p in model.parameters() if p.requires_grad))

                                # ---------- 4) 权重共享的实证: 同一核在整张图滑动 ----------
                                with torch.no_grad():
                                    model.conv1.weight.zero_()
                                    model.conv1.bias.zero_()
                                    model.conv1.weight[0, 0, 1, 1] = 1.0 # 第 0 个核 = 取单点
                                    probe = torch.zeros(1, 3, 5, 5)
                                    probe[0, 0, 2, 3] = 7.0
                                    out = model.conv1(probe) # 等宽卷积: 5x5 -> 5x5
                                    pos = (out[0, 0] == out[0, 0].max()).nonzero()[0].tolist()
                                    print("等宽卷积输出形状:", tuple(out.shape), "最大值出现在", tuple(pos))
                                    assert out.shape[-2:] == (5, 5)

                                    # ---------- 5) 转置卷积: 上采样, 输出尺寸 = (i-1)*s - 2p + k + output_padding ----------
                                    deconv = nn.ConvTranspose2d(16, 8, kernel_size=3, stride=2, padding=1, output_padding=1)
                                    up = deconv(torch.randn(1, 16, 8, 8))
                                    print("ConvTranspose2d: 8 ->", tuple(up.shape[-2:]), "(期望 16)")
                                    assert up.shape[-2:] == (16, 16)

                                    print("\nall checks passed")
```

**代码里几个必须知道的细节**：(1) `nn.Conv2d` 的权重形状是 `(out_channels, in_channels, kH, kW)`，**不是** `(kH, kW, in, out)`——教材的四维张量 $\boldsymbol{W}\in\mathbb{R}^{K\times K\times D\times D'}$ 是数学记法，落到 PyTorch 要换轴序；(2) `nn.MaxPool2d(2, 2)` 不做上取整，$32\to16$，若输入是奇数（如 31）会按 floor 变成 15；(3) `flatten(1)` 只压平 $C,H,W$ 三维并保留 batch 维；(4) 转置卷积要精确翻倍（$8\to16$）时，当 $k=3,s=2,p=1$ 必须加 `output_padding=1`，否则得到 $15$；(5) 手动改权重验证权重共享时，必须先 `zero_` 再赋值，且放在 `torch.no_grad` 下以免污染计算图。

## 验证理解

- 合上正文，用自己的话解释本知识点解决的问题及适用边界。
- 若本节含代码、公式或流程，先预测结果，再运行、推导或逐步追踪；项目片段需要沿用原文的依赖与数据。
- 如果缺少变量、术语或完整代码，请查阅[综合原文](../../../../../04-dl/03-CNN与视觉/05-CNN卷积神经网络.md)；代码片段不等同于独立可运行项目。

## 自测与关联复习

- 「-CNN卷积神经网络：可运行示例」为什么需要这种设计？改变一个条件会怎样？
- 找出仍讲不清楚的地方，加入待复习并留下具体问题。
- [本主题目录](../index.md) · [完整示例、常见坑与原文自测](../../../../../04-dl/03-CNN与视觉/05-CNN卷积神经网络.md)
