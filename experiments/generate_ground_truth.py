#!/usr/bin/env python3
"""Generate ground-truth reference annotations using semantic understanding.

These annotations are manually curated by the agent based on reading each
reference entry and applying human-level parsing to identify author, title,
year, and container (venue/journal).

Output format matches persist_references items.
"""

from __future__ import annotations

import json
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent / "ground_truth"

# ===========================================================================
# 8PP8HQMY — RT-DETRv2 (author-year, 17 entries)
# ===========================================================================

RTDETRV2 = {
    "source_file": "tests/fixtures/reference_samples/8PP8HQMY_RT-DETRv2_ Improved Baseline with Bag-of-Freebies for Real-Time Detection Transf.txt",
    "entry_style": "author-year",
    "items": [
        {
            "entry_index": 0,
            "author": ["Shahin Atakishiyev", "Mohammad Salameh", "Hengshuai Yao", "Randy Goebel"],
            "title": "Explainable artificial intelligence for autonomous driving: A comprehensive overview and field guide for future research directions",
            "year": 2024,
            "container": "IEEE Access",
            "raw": "Shahin Atakishiyev, Mohammad Salameh, Hengshuai Yao, and Randy Goebel. Explainable artificial intelligence for autonomous driving: A comprehensive overview and field guide for future research directions. IEEE Access, 2024.",
            "confidence": 0.95,
        },
        {
            "entry_index": 1,
            "author": ["Joseph Redmon", "Ali Farhadi"],
            "title": "Yolo9000: better, faster, stronger",
            "year": 2017,
            "container": "Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition",
            "raw": "Joseph Redmon and Ali Farhadi. Yolo9000: better, faster, stronger. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 7263–7271, 2017.",
            "confidence": 0.95,
        },
        {
            "entry_index": 2,
            "author": ["Joseph Redmon", "Ali Farhadi"],
            "title": "Yolov3: An incremental improvement",
            "year": 2018,
            "container": "arXiv preprint arXiv:1804.02767",
            "raw": "Joseph Redmon and Ali Farhadi. Yolov3: An incremental improvement. arXiv preprint arXiv:1804.02767, 2018.",
            "confidence": 0.95,
        },
        {
            "entry_index": 3,
            "author": ["Alexey Bochkovskiy", "Chien-Yao Wang", "Hong-Yuan Mark Liao"],
            "title": "Yolov4: Optimal speed and accuracy of object detection",
            "year": 2020,
            "container": "arXiv preprint arXiv:2004.10934",
            "raw": "Alexey Bochkovskiy, Chien-Yao Wang, and Hong-Yuan Mark Liao. Yolov4: Optimal speed and accuracy of object detection. arXiv preprint arXiv:2004.10934, 2020.",
            "confidence": 0.95,
        },
        {
            "entry_index": 4,
            "author": ["Glenn Jocher"],
            "title": "Yolov5 release v7.0",
            "year": 2022,
            "container": "https://github.com/ultralytics/yolov5/tree/v7.0",
            "raw": "Jocher Glenn. Yolov5 release v7.0. https: // github. com/ ultralytics/ yolov5/ tree/ v7. 0 , 2022.",
            "confidence": 0.85,
        },
        {
            "entry_index": 5,
            "author": ["Shangliang Xu", "Xinxin Wang", "Wenyu Lv", "Qinyao Chang", "Cheng Cui", "Kaipeng Deng", "Guanzhong Wang", "Qingqing Dang", "Shengyu Wei", "Yuning Du"],
            "title": "Pp-yoloe: An evolved version of yolo",
            "year": 2022,
            "container": "arXiv preprint arXiv:2203.16250",
            "raw": "Shangliang Xu, Xinxin Wang, Wenyu Lv, Qinyao Chang, Cheng Cui, Kaipeng Deng, Guanzhong Wang, Qingqing Dang, Shengyu Wei, Yuning Du, et al. Pp-yoloe: An evolved version of yolo. arXiv preprint arXiv:2203.16250, 2022.",
            "confidence": 0.95,
        },
        {
            "entry_index": 6,
            "author": ["Chuyi Li", "Lulu Li", "Yifei Geng", "Hongliang Jiang", "Meng Cheng", "Bo Zhang", "Zaidan Ke", "Xiaoming Xu", "Xiangxiang Chu"],
            "title": "Yolov6 v3.0: A full-scale reloading",
            "year": 2023,
            "container": "arXiv preprint arXiv:2301.05586",
            "raw": "Chuyi Li, Lulu Li, Yifei Geng, Hongliang Jiang, Meng Cheng, Bo Zhang, Zaidan Ke, Xiaoming Xu, and Xiangxiang Chu. Yolov6 v3.0: A full-scale reloading. arXiv preprint arXiv:2301.05586, 2023.",
            "confidence": 0.95,
        },
        {
            "entry_index": 7,
            "author": ["Chien-Yao Wang", "Alexey Bochkovskiy", "Hong-Yuan Mark Liao"],
            "title": "Yolov7: Trainable bag-of-freebies sets new state-of-the-art for real-time object detectors",
            "year": 2023,
            "container": "Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition",
            "raw": "Chien-Yao Wang, Alexey Bochkovskiy, and Hong-Yuan Mark Liao. Yolov7: Trainable bag-of-freebies sets new stateof-the-art for real-time object detectors. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 7464–7475, 2023.",
            "confidence": 0.95,
        },
        {
            "entry_index": 8,
            "author": ["Glenn Jocher"],
            "title": "Yolov8",
            "year": 2023,
            "container": "https://github.com/ultralytics/ultralytics/tree/main",
            "raw": "Jocher Glenn. Yolov8. https: // github. com/ ultralytics/ ultralytics/ tree/ main , 2023.",
            "confidence": 0.80,
        },
        {
            "entry_index": 9,
            "author": ["Chien-Yao Wang", "I-Hau Yeh", "Hong-Yuan Mark Liao"],
            "title": "Yolov9: Learning what you want to learn using programmable gradient information",
            "year": 2024,
            "container": "arXiv preprint arXiv:2402.13616",
            "raw": "Chien-Yao Wang, I-Hau Yeh, and Hong-Yuan Mark Liao. Yolov9: Learning what you want to learn using programmable gradient information. arXiv preprint arXiv:2402.13616, 2024a.",
            "confidence": 0.95,
        },
        {
            "entry_index": 10,
            "author": ["Ao Wang", "Hui Chen", "Lihao Liu", "Kai Chen", "Zijia Lin", "Jungong Han", "Guiguang Ding"],
            "title": "Yolov10: Real-time end-to-end object detection",
            "year": 2024,
            "container": "arXiv preprint arXiv:2405.14458",
            "raw": "Ao Wang, Hui Chen, Lihao Liu, Kai Chen, Zijia Lin, Jungong Han, and Guiguang Ding. Yolov10: Real-time end-toend object detection. arXiv preprint arXiv:2405.14458, 2024b.",
            "confidence": 0.95,
        },
        {
            "entry_index": 11,
            "author": ["Yian Zhao", "Wenyu Lv", "Shangliang Xu", "Jinman Wei", "Guanzhong Wang", "Qingqing Dang", "Yi Liu", "Jie Chen"],
            "title": "Detrs beat yolos on real-time object detection",
            "year": 2024,
            "container": "Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition",
            "raw": "Yian Zhao, Wenyu Lv, Shangliang Xu, Jinman Wei, Guanzhong Wang, Qingqing Dang, Yi Liu, and Jie Chen. Detrs beat yolos on real-time object detection. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 16965–16974, 2024.",
            "confidence": 0.95,
        },
        {
            "entry_index": 12,
            "author": ["Nicolas Carion", "Francisco Massa", "Gabriel Synnaeve", "Nicolas Usunier", "Alexander Kirillov", "Sergey Zagoruyko"],
            "title": "End-to-end object detection with transformers",
            "year": 2020,
            "container": "European Conference on Computer Vision (ECCV)",
            "raw": "Nicolas Carion, Francisco Massa, Gabriel Synnaeve, Nicolas Usunier, Alexander Kirillov, and Sergey Zagoruyko. Endto-end object detection with transformers. In European Conference on Computer Vision, pages 213–229. Springer, 2020.",
            "confidence": 0.95,
        },
        {
            "entry_index": 13,
            "author": ["Xizhou Zhu", "Weijie Su", "Lewei Lu", "Bin Li", "Xiaogang Wang", "Jifeng Dai"],
            "title": "Deformable detr: Deformable transformers for end-to-end object detection",
            "year": 2020,
            "container": "International Conference on Learning Representations (ICLR)",
            "raw": "Xizhou Zhu, Weijie Su, Lewei Lu, Bin Li, Xiaogang Wang, and Jifeng Dai. Deformable detr: Deformable transformers for end-to-end object detection. In International Conference on Learning Representations, 2020.",
            "confidence": 0.95,
        },
        {
            "entry_index": 14,
            "author": ["Kaiming He", "Xiangyu Zhang", "Shaoqing Ren", "Jian Sun"],
            "title": "Deep residual learning for image recognition",
            "year": 2016,
            "container": "Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)",
            "raw": "Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Deep residual learning for image recognition. In Proceedings of the IEEE conference on computer vision and pattern recognition, pages 770–778, 2016.",
            "confidence": 0.95,
        },
        {
            "entry_index": 15,
            "author": ["Ilya Loshchilov", "Frank Hutter"],
            "title": "Decoupled weight decay regularization",
            "year": 2018,
            "container": "International Conference on Learning Representations (ICLR)",
            "raw": "Ilya Loshchilov and Frank Hutter. Decoupled weight decay regularization. In International Conference on Learning Representations, 2018.",
            "confidence": 0.95,
        },
        {
            "entry_index": 16,
            "author": ["Tsung-Yi Lin", "Michael Maire", "Serge Belongie", "James Hays", "Pietro Perona", "Deva Ramanan", "Piotr Dollár", "C. Lawrence Zitnick"],
            "title": "Microsoft coco: Common objects in context",
            "year": 2014,
            "container": "European Conference on Computer Vision (ECCV)",
            "raw": "Tsung-Yi Lin, Michael Maire, Serge Belongie, James Hays, Pietro Perona, Deva Ramanan, Piotr Dollár, and C Lawrence Zitnick. Microsoft coco: Common objects in context. In European Conference on Computer Vision, pages 740–755. Springer, 2014.",
            "confidence": 0.95,
        },
    ],
}


# ===========================================================================
# 8ET4QJ6S — U-Net (mixed, 14 entries, includes web URLs)
# ===========================================================================

UNET = {
    "source_file": "tests/fixtures/reference_samples/8ET4QJ6S_U-Net_ Convolutional Networks for Biomedical Image Segmentation.txt",
    "entry_style": "mixed",
    "items": [
        {
            "entry_index": 0,
            "author": ["Dan C. Ciresan", "Luca M. Gambardella", "Alessandro Giusti", "Jürgen Schmidhuber"],
            "title": "Deep neural networks segment neuronal membranes in electron microscopy images",
            "year": 2012,
            "container": "Advances in Neural Information Processing Systems (NIPS)",
            "raw": "Ciresan, D.C., Gambardella, L.M., Giusti, A., Schmidhuber, J.: Deep neural networks segment neuronal membranes in electron microscopy images. In: NIPS. pp. 2852–2860 (2012)",
            "confidence": 0.95,
        },
        {
            "entry_index": 1,
            "author": ["Alexey Dosovitskiy", "Jost Tobias Springenberg", "Martin Riedmiller", "Thomas Brox"],
            "title": "Discriminative unsupervised feature learning with convolutional neural networks",
            "year": 2014,
            "container": "Advances in Neural Information Processing Systems (NIPS)",
            "raw": "Dosovitskiy, A., Springenberg, J.T., Riedmiller, M., Brox, T.: Discriminative unsupervised feature learning with convolutional neural networks. In: NIPS (2014)",
            "confidence": 0.90,
        },
        {
            "entry_index": 2,
            "author": ["Ross Girshick", "Jeff Donahue", "Trevor Darrell", "Jitendra Malik"],
            "title": "Rich feature hierarchies for accurate object detection and semantic segmentation",
            "year": 2014,
            "container": "Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)",
            "raw": "Girshick, R., Donahue, J., Darrell, T., Malik, J.: Rich feature hierarchies for accurate object detection and semantic segmentation. In: Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR) (2014)",
            "confidence": 0.90,
        },
        {
            "entry_index": 3,
            "author": ["Bharath Hariharan", "Pablo Arbeláez", "Ross Girshick", "Jitendra Malik"],
            "title": "Hypercolumns for object segmentation and fine-grained localization",
            "year": 2014,
            "container": "arXiv:1411.5752 [cs.CV]",
            "raw": "Hariharan, B., Arbelez, P., Girshick, R., Malik, J.: Hypercolumns for object segmentation and fine-grained localization (2014), arXiv:1411.5752 [cs.CV]",
            "confidence": 0.88,
        },
        {
            "entry_index": 4,
            "author": ["Kaiming He", "Xiangyu Zhang", "Shaoqing Ren", "Jian Sun"],
            "title": "Delving deep into rectifiers: Surpassing human-level performance on imagenet classification",
            "year": 2015,
            "container": "arXiv:1502.01852 [cs.CV]",
            "raw": "He, K., Zhang, X., Ren, S., Sun, J.: Delving deep into rectifiers: Surpassing humanlevel performance on imagenet classification (2015), arXiv:1502.01852 [cs.CV]",
            "confidence": 0.90,
        },
        {
            "entry_index": 5,
            "author": ["Yangqing Jia", "Evan Shelhamer", "Jeff Donahue", "Sergey Karayev", "Jonathan Long", "Ross Girshick", "Sergio Guadarrama", "Trevor Darrell"],
            "title": "Caffe: Convolutional architecture for fast feature embedding",
            "year": 2014,
            "container": "arXiv:1408.5093 [cs.CV]",
            "raw": "Jia, Y., Shelhamer, E., Donahue, J., Karayev, S., Long, J., Girshick, R., Guadarrama, S., Darrell, T.: Caffe: Convolutional architecture for fast feature embedding (2014), arXiv:1408.5093 [cs.CV]",
            "confidence": 0.90,
        },
        {
            "entry_index": 6,
            "author": ["Alex Krizhevsky", "Ilya Sutskever", "Geoffrey E. Hinton"],
            "title": "Imagenet classification with deep convolutional neural networks",
            "year": 2012,
            "container": "Advances in Neural Information Processing Systems (NIPS)",
            "raw": "Krizhevsky, A., Sutskever, I., Hinton, G.E.: Imagenet classification with deep convolutional neural networks. In: NIPS. pp. 1106–1114 (2012)",
            "confidence": 0.95,
        },
        {
            "entry_index": 7,
            "author": ["Yann LeCun", "Bernhard Boser", "John S. Denker", "Donnie Henderson", "Richard E. Howard", "Wayne Hubbard", "Lawrence D. Jackel"],
            "title": "Backpropagation applied to handwritten zip code recognition",
            "year": 1989,
            "container": "Neural Computation",
            "raw": "LeCun, Y., Boser, B., Denker, J.S., Henderson, D., Howard, R.E., Hubbard, W., Jackel, L.D.: Backpropagation applied to handwritten zip code recognition. Neural Computation 1(4), 541–551 (1989)",
            "confidence": 0.95,
        },
        {
            "entry_index": 8,
            "author": ["Jonathan Long", "Evan Shelhamer", "Trevor Darrell"],
            "title": "Fully convolutional networks for semantic segmentation",
            "year": 2014,
            "container": "arXiv:1411.4038 [cs.CV]",
            "raw": "Long, J., Shelhamer, E., Darrell, T.: Fully convolutional networks for semantic segmentation (2014), arXiv:1411.4038 [cs.CV]",
            "confidence": 0.90,
        },
        {
            "entry_index": 9,
            "author": ["Martin Maška"],
            "title": "A benchmark for comparison of cell tracking algorithms",
            "year": 2014,
            "container": "Bioinformatics",
            "raw": "Maska, M., (...), de Solorzano, C.O.: A benchmark for comparison of cell tracking algorithms. Bioinformatics 30, 1609–1617 (2014)",
            "confidence": 0.85,
        },
        {
            "entry_index": 10,
            "author": ["Mojtaba Seyedhosseini", "Mehdi Sajjadi", "Tolga Tasdizen"],
            "title": "Image segmentation with cascaded hierarchical models and logistic disjunctive normal networks",
            "year": 2013,
            "container": "Proceedings of the IEEE International Conference on Computer Vision (ICCV)",
            "raw": "Seyedhosseini, M., Sajjadi, M., Tasdizen, T.: Image segmentation with cascaded hierarchical models and logistic disjunctive normal networks. In: Computer Vision (ICCV), 2013 IEEE International Conference on. pp. 2168–2175 (2013)",
            "confidence": 0.88,
        },
        {
            "entry_index": 11,
            "author": ["Karen Simonyan", "Andrew Zisserman"],
            "title": "Very deep convolutional networks for large-scale image recognition",
            "year": 2014,
            "container": "arXiv:1409.1556 [cs.CV]",
            "raw": "Simonyan, K., Zisserman, A.: Very deep convolutional networks for large-scale image recognition (2014), arXiv:1409.1556 [cs.CV]",
            "confidence": 0.90,
        },
        {
            "entry_index": 12,
            "author": [],
            "title": "Web page of the cell tracking challenge",
            "year": None,
            "container": "http://www.codesolorzano.com/celltrackingchallenge/Cell_Tracking_Challenge/Welcome.html",
            "raw": "WWW: Web page of the cell tracking challenge, http://www.codesolorzano.com/ celltrackingchallenge/Cell\\_Tracking\\_Challenge/Welcome.html",
            "confidence": 0.70,
        },
        {
            "entry_index": 13,
            "author": [],
            "title": "Web page of the EM segmentation challenge",
            "year": None,
            "container": "http://brainiac2.mit.edu/isbi_challenge/",
            "raw": "WWW: Web page of the em segmentation challenge, http://brainiac2.mit.edu/ isbi\\_challenge/",
            "confidence": 0.70,
        },
    ],
}


# ===========================================================================
# NXLIGKF5 — DN-DETR (mixed with numeric prefixes, some grouped entries in single lines, 21 raw entries)
# ===========================================================================

DNDETR = {
    "source_file": "tests/fixtures/reference_samples/NXLIGKF5_DN-DETR_ accelerate DETR training by introducing query DeNoising.txt",
    "entry_style": "mixed",
    "items": [
        {
            "entry_index": 0,
            "author": ["Nicolas Carion", "Francisco Massa", "Gabriel Synnaeve", "Nicolas Usunier", "Alexander Kirillov", "Sergey Zagoruyko"],
            "title": "End-to-end object detection with transformers",
            "year": 2020,
            "container": "European Conference on Computer Vision (ECCV)",
            "raw": "[1] Nicolas Carion,Francisco Massa, Gabriel Synnaeve,Nicolas Usunier, Alexander Kirillov,and Sergey Zagoruyko. End-toend object detection with transformers. In European Conference on Computer Vision, pages 213-229. Springer, 2020.",
            "confidence": 0.95,
        },
        {
            "entry_index": 1,
            "author": ["Ting Chen", "Saurabh Saxena", "Lala Li", "David J. Fleet", "Geoffrey Hinton"],
            "title": "Pix2seq: A language modeling framework for object detection",
            "year": 2021,
            "container": "arXiv preprint",
            "raw": "[2] Ting Chen, Saurabh Saxena,LalaLi, David J. Fleet,and Geoffrey Hinton. Pix2seq: A language modeling framework for object detection, 2021.",
            "confidence": 0.88,
        },
        {
            "entry_index": 2,
            "author": ["Xiyang Dai", "Yinpeng Chen", "Jianwei Yang", "Pengchuan Zhang", "Lu Yuan", "Lei Zhang"],
            "title": "Dynamic detr: End-to-end object detection with dynamic attention",
            "year": 2021,
            "container": "Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)",
            "raw": "[3] Xiyang Dai，Yinpeng Chen，Jianwei Yang，Pengchuan Zhang,Lu Yuan,and Lei Zhang. Dynamic detr: End-to-end object detection with dynamic attention. In Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV), pages 2988-2997, October 2021.",
            "confidence": 0.95,
        },
        {
            "entry_index": 3,
            "author": ["Xiyang Dai", "Yinpeng Chen", "Jianwei Yang", "Pengchuan Zhang", "Lu Yuan", "Lei Zhang"],
            "title": "Dynamic detr: End-to-end object detection with dynamic attention",
            "year": 2021,
            "container": "Proceedings of the IEEE/CVF International Conference on Computer Vision",
            "raw": "[4] Xiyang Dai，Yinpeng Chen，Jianwei Yang，Pengchuan Zhang,Lu Yuan,and Lei Zhang.Dynamic detr: End-toend object detection with dynamic attention.In Proceedings of the IEEE/CVF International Conference on Computer Vision, pages 2988-2997,2021.",
            "confidence": 0.92,
        },
        {
            "entry_index": 4,
            "author": ["Enrico Maria Fenoaltea", "Izat B. Baybusinov", "Jianyang Zhao", "Lei Zhou", "Yi-Cheng Zhang"],
            "title": "The stable marriage problem: An interdisciplinary review from the physicist's perspective",
            "year": 2021,
            "container": "Physics Reports",
            "raw": "[5] Enrico Maria Fenoaltea, Izat B Baybusinov, Jianyang Zhao, Lei Zhou,and Yi-Cheng Zhang. The stable marriage problem: An interdisciplinary review from the physicist's perspective.Physics Reports,2021.",
            "confidence": 0.92,
        },
        {
            "entry_index": 5,
            "author": ["Peng Gao", "Minghang Zheng", "Xiaogang Wang", "Jifeng Dai", "Hongsheng Li"],
            "title": "Fast convergence of detr with spatially modulated co-attention",
            "year": 2021,
            "container": "arXiv preprint arXiv:2101.07448",
            "raw": "[6] Peng Gao,Minghang Zheng, Xiaogang Wang, Jifeng Dai, and Hongsheng Li. Fast convergence of detr with spatially modulated co-attention. arXiv preprint arXiv:2101.07448, 2021.",
            "confidence": 0.95,
        },
        {
            "entry_index": 6,
            "author": ["Ross Girshick", "Jeff Donahue", "Trevor Darrell", "Jitendra Malik"],
            "title": "Rich feature hierarchies for accurate object detection and semantic segmentation",
            "year": 2014,
            "container": "arXiv preprint",
            "raw": "[7] Ross Girshick,Jeff Donahue,Trevor Darrell,and Jitendra Malik. Rich feature hierarchies for accurate object detection and semantic segmentation, 2014.",
            "confidence": 0.88,
        },
        {
            "entry_index": 7,
            "author": ["Kaiming He", "Xiangyu Zhang", "Shaoqing Ren", "Jian Sun"],
            "title": "Deep residual learning for image recognition",
            "year": 2016,
            "container": "Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)",
            "raw": "[8] Kaiming He, Xiangyu Zhang,Shaoqing Ren,and Jian Sun. Deep residual learning for image recognition. In 2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR), pages 770-778,2016.",
            "confidence": 0.95,
        },
        {
            "entry_index": 8,
            "author": ["Tsung-Yi Lin", "Priya Goyal", "Ross Girshick", "Kaiming He", "Piotr Dollár"],
            "title": "Focal loss for dense object detection",
            "year": 2018,
            "container": "arXiv preprint",
            "raw": "[9] Tsung-YiLin, Priya Goyal, Ross Girshick, Kaiming He,and Piotr Dollar. Focal loss for dense object detection,2018.",
            "confidence": 0.88,
        },
        {
            "entry_index": 9,
            "author": ["Tsung-Yi Lin", "Michael Maire", "Serge Belongie", "James Hays", "Pietro Perona", "Deva Ramanan", "Piotr Dollár", "C. Lawrence Zitnick"],
            "title": "Microsoft coco: Common objects in context",
            "year": 2014,
            "container": "European Conference on Computer Vision (ECCV)",
            "raw": "[10] Tsung-Yi Lin,Michael Maire,Serge Belongie, James Hays, Pietro Perona, Deva Ramanan, Piotr Dollar, and C Lawrence Zitnick.Microsoft coco: Common objects in context.In European conference on computer vision, pages 740-755. Springer, 2014.",
            "confidence": 0.95,
        },
        {
            "entry_index": 10,
            "author": ["Shilong Liu", "Feng Li", "Hao Zhang", "Xiao Yang", "Xianbiao Qi", "Hang Su", "Jun Zhu", "Lei Zhang"],
            "title": "DAB-DETR: Dynamic anchor boxes are better queries for DETR",
            "year": 2022,
            "container": "International Conference on Learning Representations (ICLR)",
            "raw": "[11] Shilong Liu,Feng Li, Hao Zhang, Xiao Yang, Xianbiao Qi, Hang Su, Jun Zhu, and Lei Zhang. DAB-DETR: Dynamic anchor boxes are better queries for DETR.In International Conference on Learning Representations, 2022.",
            "confidence": 0.95,
        },
        {
            "entry_index": 11,
            "author": ["Depu Meng", "Xiaokang Chen", "Zejia Fan", "Gang Zeng", "Houqiang Li", "Yuhui Yuan", "Lei Sun", "Jingdong Wang"],
            "title": "Conditional detr for fast training convergence",
            "year": 2021,
            "container": "arXiv preprint arXiv:2108.06152",
            "raw": "[12] Depu Meng, Xiaokang Chen, Zejia Fan,Gang Zeng, Houqiang Li, Yuhui Yuan, Lei Sun,and Jingdong Wang. Conditional detr for fast training convergence. arXiv preprint arXiv:2108.06152,2021.",
            "confidence": 0.95,
        },
        {
            "entry_index": 12,
            "author": ["Joseph Redmon", "Ali Farhadi"],
            "title": "Yolo9000: Better, faster, stronger",
            "year": 2016,
            "container": "Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)",
            "raw": "[13] Joseph Redmon and Ali Farhadi. Yolo90oO:Better,faster, stronger, 2016.",
            "confidence": 0.88,
        },
        {
            "entry_index": 13,
            "author": ["Joseph Redmon", "Ali Farhadi"],
            "title": "Yolov3: An incremental improvement",
            "year": 2018,
            "container": "arXiv preprint",
            "raw": "[14] Joseph Redmon and Ali Farhadi． Yolov3:An incremental improvement, 2018.",
            "confidence": 0.88,
        },
        {
            "entry_index": 14,
            "author": ["Shaoqing Ren", "Kaiming He", "Ross Girshick", "Jian Sun"],
            "title": "Faster r-cnn: Towards real-time object detection with region proposal networks",
            "year": 2017,
            "container": "IEEE Transactions on Pattern Analysis and Machine Intelligence",
            "raw": "[15] Shaoqing Ren,Kaiming He,Ross Girshick,and Jian Sun. Faster r-cnn: Towards real-time object detection with region proposal networks. IEEE Transactions on Pattern Analysis and Machine Intelligence. 39(6):1137-1149.2017.",
            "confidence": 0.95,
        },
        {
            "entry_index": 15,
            "author": ["Zhiqing Sun", "Shengcao Cao", "Yiming Yang", "Kris Kitani"],
            "title": "Rethinking transformer-based set prediction for object detection",
            "year": 2020,
            "container": "arXiv preprint arXiv:2011.10881",
            "raw": "[16] Zhiqing Sun, Shengcao Cao,Yiming Yang,and Kris Kitani. Rethinking transformer-based set prediction for object detection.arXiv preprint arXiv:2011.10881,2020.",
            "confidence": 0.95,
        },
        {
            "entry_index": 16,
            "author": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez", "Lukasz Kaiser", "Illia Polosukhin"],
            "title": "Attention is all you need",
            "year": 2017,
            "container": "Advances in Neural Information Processing Systems (NeurIPS)",
            "raw": "[17] AshishVaswani,Noam Shazeer,NikiParmar,JakobUszkoreit,Llion Jones,Aidan NGomez,Lukasz Kaiser,and Illia Polosukhin. Attention is all you need. In Advances in neural information processing systems,pages 5998-6008,2017.",
            "confidence": 0.95,
        },
        {
            "entry_index": 17,
            "author": ["Yingming Wang", "Xiangyu Zhang", "Tong Yang", "Jian Sun"],
            "title": "Anchor detr: Query design for transformer-based detector",
            "year": 2021,
            "container": "arXiv preprint arXiv:2109.07107",
            "raw": "[18] Yingming Wang,Xiangyu Zhang, Tong Yang,and Jian Sun. Anchor detr: Query design for transformer-based detector. arXiv preprint arXiv:2109.07107,2021.",
            "confidence": 0.95,
        },
        {
            "entry_index": 18,
            "author": ["Zhuyu Yao", "Jiangbo Ai", "Boxun Li", "Chi Zhang"],
            "title": "Efficient detr: Improving end-to-end object detector with dense prior",
            "year": 2021,
            "container": "arXiv preprint arXiv:2104.01318",
            "raw": "[19] Zhuyu Yao,Jiangbo Ai,Boxun Li,and Chi Zhang.Efficient detr: Improving end-to-end object detector with dense prior. arXiv preprint arXiv:2104.01318,2021.",
            "confidence": 0.95,
        },
        {
            "entry_index": 19,
            "author": ["Xizhou Zhu", "Weijie Su", "Lewei Lu", "Bin Li", "Xiaogang Wang", "Jifeng Dai"],
            "title": "Deformable detr: Deformable transformers for end-to-end object detection",
            "year": 2021,
            "container": "International Conference on Learning Representations (ICLR)",
            "raw": "[20] Xizhou Zhu, Weijie Su,Lewei Lu, Bin Li, Xiaogang Wang, and Jifeng Dai.Deformable detr:Deformable transformers for end-to-end object detection.In ICLR 2021: The Ninth International Conference on Learning Representations,2021.",
            "confidence": 0.95,
        },
    ],
}


# ===========================================================================
# Write outputs
# ===========================================================================

ALL = {
    "8PP8HQMY_RT-DETRv2": RTDETRV2,
    "8ET4QJ6S_U-Net": UNET,
    "NXLIGKF5_DN-DETR": DNDETR,
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for slug, data in ALL.items():
        # Add schema version
        data["schema"] = "reference_ground_truth.v1"

        path = OUTPUT_DIR / f"{slug}_ground_truth.json"
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  {slug}: {len(data['items'])} entries → {path.name}")

    print(f"\nGround truth files written to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
