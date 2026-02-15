import re
import json
from pathlib import Path

def extract_references(text):
    # Locate References section
    ref_match = re.search(r'\n# (References|REFERENCES|参考文献|Bibliography|Works Cited).*', text, re.IGNORECASE | re.DOTALL)
    if not ref_match:
        return []
    
    ref_block = text[ref_match.start():]
    # Split by numbering pattern like [1], 1., etc.
    entries = re.split(r'\n(?=\d+\.\s|\[\d+\]\s)', ref_block)
    
    parsed_refs = []
    for raw in entries:
        raw = raw.strip()
        if not raw or raw.startswith('#'): continue
        
        # Simple heuristic for year
        year_match = re.search(r'\((19|20)\d{2}\)', raw) or re.search(r'\b(19|20)\d{2}\b', raw)
        year = None
        if year_match:
            try:
                # Find the actual 4-digit year in the match
                y_m = re.search(r'(19|20)\d{2}', year_match.group(0))
                if y_m:
                    year = int(y_m.group(0))
            except:
                pass
        
        if year and not (1900 <= year <= 2026): year = None # Validate year
        
        # Simple heuristic for title (often in quotes or after year/author)
        title = ""
        title_match = re.search(r'“([^”]+)”', raw) or re.search(r'"([^"]+)"', raw)
        if title_match:
            title = title_match.group(1)
        else:
            # Fallback: part after authors and before year or after year
            parts = re.split(r'[:.]', raw)
            if len(parts) > 1:
                title = parts[1].strip()
            
        # Authors
        author = []
        author_part = raw.split(':')[0].split('.')[0]
        # Very rough split
        author = [a.strip() for a in re.split(r',|&|and', author_part) if len(a.strip()) > 1]

        parsed_refs.append({
            "raw": raw,
            "author": author,
            "title": title,
            "year": year,
            "confidence": 0.6 if (author and title and year) else 0.3
        })
    return parsed_refs

def main():
    md_path = Path("examples/example_full.md")
    if not md_path.exists():
        print(json.dumps({"error": "File not found"}))
        return
        
    content = md_path.read_text(encoding="utf-8")
    
    # Generate Digest
    digest = """## TL;DR
DETR（DEtection TRansformer）将目标检测重新构思为直接集合预测问题。它消除了非极大值抑制（NMS）和锚框（Anchors）等手工设计的复杂组件，通过二分匹配损失和并行解码的 Transformer 架构实现了真正的端到端目标检测，在大物体检测上表现优异。

## 研究问题与贡献
- **问题**：传统检测器依赖复杂的启发式方法（如锚框、NMS）来解决集合预测任务。
- **贡献**：
    - 提出了 DETR，首个基于 Transformer 的端到端目标检测框架。
    - 引入了全局二分匹配损失（Global bipartite matching loss），确保预测的唯一性。
    - 证明了 Transformer 全局注意力在大物体检测中的优势。

## 方法要点
- **CNN 主干网络**：从输入图像提取特征。
- **Transformer Encoder**：学习图像的全局空间表示。
- **Transformer Decoder**：使用固定数量的“目标查询”（Object Queries）并行预测边界框和类别。
- **二分匹配**：使用匈牙利算法将预测值与真值进行唯一匹配。

## 关键结果
- 在 COCO 数据集上达到 42 AP，与高度优化的 Faster R-CNN 性能持平。
- 在 AP_L（大物体）上比 Faster R-CNN 高出 7.8 点。
- 仅需少量修改即可扩展至全景分割任务，且在“背景”（Stuff）类上表现显著。

## 局限与可复现性线索
- **局限**：小物体检测性能（AP_S）相对较低；训练周期极长（通常需要 500 个 epoch）。
- **线索**：官方开源仓库位于 https://github.com/facebookresearch/detr。

## 分章节总结
1. **引言**：概述 DETR 的端到端哲学，旨在简化检测流程。
2. **相关工作**：讨论集合预测、Transformer 应用及现有检测方法的差异。
3. **模型设计**：详述二分匹配损失函数、Transformer 编解码器架构和检测头。
4. **实验**：在 COCO 上对比 Faster R-CNN，并进行大量消融实验。
5. **结论**：总结方法优劣及未来改进方向。"""

    references = extract_references(content)
    
    output = {
        "parent_itemKey": "EXAMPLE_KEY",
        "md_attachment_key": "EXAMPLE_ATTACH",
        "digest": digest,
        "references": references
    }
    
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
