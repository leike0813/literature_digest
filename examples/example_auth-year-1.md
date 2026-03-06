# DAB-DETR: DYNAMIC ANCHOR BOXES ARE BETTER QUERIES FOR DETR

Shilong Liu $^{1,2*}$ , Feng Li $^{2,3}$ , Hao Zhang $^{2,3}$ , Xiao Yang $^{1}$ , Xianbiao Qi $^{2}$ , Hang Su $^{1,4}$ , Jun Zhu $^{1,4\dagger}$ , Lei Zhang $^{2\dagger}$

$^{1}$ Dept. of Comp. Sci. and Tech., BNRist Center, State Key Lab for Intell. Tech. & Sys., Institute for AI, Tsinghua-Bosch Joint Center for ML, Tsinghua University.

$^{2}$ International Digital Economy Academy (IDEA).

$^{3}$ Hong Kong University of Science and Technology.

$^{4}$ Peng Cheng Laboratory, Shenzhen, Guangdong, China.

{liusl20, yangxiao19}@mails.tsinghua.edu.cn

{fliay,hzhangcx}@connect.ust.hk

{qixianbiao,leizhang}@idea.edu.cn

{suhangss, dcszj}@mail.tsinghua.edu.cn

# ABSTRACT

We present in this paper a novel query formulation using dynamic anchor boxes for DETR (DEtection Transformer) and offer a deeper understanding of the role of queries in DETR. This new formulation directly uses box coordinates as queries in Transformer decoders and dynamically updates them layer-by-layer. Using box coordinates not only helps using explicit positional priors to improve the query-to-feature similarity and eliminate the slow training convergence issue in DETR, but also allows us to modulate the positional attention map using the box width and height information. Such a design makes it clear that queries in DETR can be implemented as performing soft ROI pooling layer-by-layer in a cascade manner. As a result, it leads to the best performance on MS-COCO benchmark among the DETR-like detection models under the same setting, e.g., AP  $45.7\%$  using ResNet50-DC5 as backbone trained in 50 epochs. We also conducted extensive experiments to confirm our analysis and verify the effectiveness of our methods. Code is available at https://github.com/SlongLiu/DAB-DETR.

# 1 INTRODUCTION

Object detection is a fundamental task in computer vision of wide applications. Most classical detectors are based on convolutional architectures which have made remarkable progress in the last decade (Ren et al., 2017; Girshick, 2015; Redmon et al., 2016; Bochkovskiy et al., 2020; Ge et al., 2021). Recently, Carion et al. (2020) proposed a Transformer-based end-to-end detector named DETR (DEtection Transformer), which eliminates the need for hand-designed components, e.g., anchors, and shows promising performance compared with modern anchor-based detectors such as Faster RCNN (Ren et al., 2017).

In contrast to anchor-based detectors, DETR models object detection as a set prediction problem and uses 100 learnable queries to probe and pool features from images, which makes predictions without the need of using non-maximum suppression. However, due to its ineffective design and use of queries, DETR suffers from significantly slow training convergence, usually requiring 500 epochs to achieve a good performance. To address this issue, many follow-up works attempted to improve the design of DETR queries for both faster training convergence and better performance (Zhu et al., 2021; Gao et al., 2021; Meng et al., 2021; Wang et al., 2021).

Despite all the progress, the role of the learned queries in DETR is still not fully understood or utilized. While most previous attempts make each query in DETR more explicitly associated with one

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/2a9293a54adceac15c40f28c902732f6212e3e9417fa5b2f007ce92cd506a4ac.jpg)  
(a) DETR

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/f213c85e19d5dae6f9b1cdb5d6ac8ed6599274ff1b9b50ce79117dce2243eeaa.jpg)  
(b) Conditional DETR

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/303b19e26bce4c78d5ea64cde9d684d0fcd1345fe5e0df40293be219056bb671.jpg)  
Figure 1: Comparison of DETR, Conditional DETR, and our proposed DAB-DETR. For clarity, we only show the cross-attention part in the Transformer decoder. (a) DETR uses the learnable queries for all the layers without any adaptation, which accounts for its slow training convergence. (b) Conditional DETR adapts the learnable queries for each layer mainly to provide a better reference query point to pool features from the image feature map. In contrast, (c) DAB-DETR directly uses dynamically updated anchor boxes to provide both a reference query point  $(x,y)$  and a reference anchor size  $(w,h)$  to improve the cross-attention computation. We marked the modules with difference in purple.  
(c) DAB-DETR

specific spatial position rather than multiple positions, the technical solutions are largely different. For example, Conditional DETR learns a conditional spatial query by adapting a query based on its content feature for better matching with image features (Meng et al., 2021). Efficient DETR introduces a dense prediction module to select top-K object queries (Yao et al., 2021) and Anchor DETR formulates queries as 2D anchor points (Wang et al., 2021), both associating each query with a specific spatial position. Similarly, Deformable DETR directly treats 2D reference points as queries and performs deformable cross-attention operation at each reference points (Zhu et al., 2021). But all the above works only leverage 2D positions as anchor points without considering of the object scales.

Motivated by these studies, we take a closer look at the cross-attention module in Transformer decoder and propose to use anchor boxes, i.e. 4D box coordinates  $(x,y,w,h)$ , as queries in DETR and update them layer-by-layer. This new query formulation introduces better spatial priors for the cross-attention module by considering both the position and size of each anchor box, which also leads to a much simpler implementation and a deeper understanding of the role of queries in DETR.

The key insight behind this formulation is that each query in DETR is formed by two parts: a content part (decoder self-attention output) and a positional part (e.g. learnable queries in DETR)<sup>1</sup>. The cross-attention weights are computed by comparing a query with a set of keys which consists of two parts as a content part (encoded image feature) and a positional part (positional embedding). Thus, queries in Transformer decoder can be interpreted as pooling features from a feature map based on the query-to-feature similarity measure, which considers both the content and positional information. While the content similarity is for pooling semantically related features, the positional similarity is to provide a positional constraint for pooling features around the query position. This attention computing mechanism motivates us to formulate queries as anchor boxes as illustrated in Fig. 1 (c), allowing us to use the center position  $(x, y)$  of an anchor box to pool features around the center and use the anchor box size  $(w, h)$  to modulate the cross-attention map, adapting it to anchor box size. In addition, because of the use of coordinates as queries, anchor boxes can be updated dynamically layer-by-layer. In this way, queries in DETR can be implemented as performing soft ROI pooling layer-by-layer in a cascade way.

We provide a better positional prior for pooling features by using anchor box size to modulate the cross-attention. Because the cross-attention can pool features from the whole feature map, it is crucial to provide a proper positional prior for each query to let the cross-attention module focus on a

local region corresponding to a target object. It can also facilitate to speed up the training convergence of DETR. Most prior works improve DETR by associating each query with a specific location, but they assume an isotropic Gaussian positional prior of a fixed size, which is inappropriate for objects of different scales. With the size information  $(w,h)$  available in each query anchor box, we can modulate the Gaussian positional prior as an oval shape. More specifically, we divide the width and height from the cross-attention weight (before softmax) for its  $x$  part and  $y$  part separately, which helps the Gaussian prior to better match with objects of different scales. To further improve the positional prior, we also introduce a temperature parameter to tune the flatness of positional attention, which has been overlooked in all prior works.

In summary, our proposed DAB-DETR (Dynamic Anchor Box DETR) presents a novel query formulation by directly learning anchors as queries. This formulation offers a deeper understanding of the role of queries, allowing us to use anchor size to modulate the positional cross-attention map in Transformer decoders and perform dynamic anchor update layer-by-layer. Our results demonstrate that DAB-DETR attains the best performance among DETR-like architectures under the same setting on the COCO object detection benchmark. The proposed method can achieve  $45.7\%$  AP when using a single ResNet-50 (He et al., 2016) model as backbone for training 50 epochs. We also conducted extensive experiments to confirm our analysis and verify the effectiveness of our methods.

# 2 RELATED WORK

Most classical detectors are anchor-based, using either anchor boxes (Ren et al., 2017; Girshick, 2015; Sun et al., 2021) or anchor points (Tian et al., 2019; Zhou et al., 2019). In contrast, DETR (Carion et al., 2020) is a fully anchor-free detector using a set of learnable vectors as queries. Many follow-up works attempted to solve the slow convergence of DETR from different perspectives. Sun et al. (2020) pointed out that the cause of slow training of DETR is due to the crossattention in decoders and hence proposed an encoder-only model. Gao et al. (2021) instead introduced a Gaussian prior to regulate the cross-attention. Despite their improved performance, they did not give a proper explanation of the slow training and the roles of queries in DETR.

Another direction to improve DETR, which is more relevant to our work, is towards a deeper understanding of the role of queries in DETR. As the learnable queries in DETR are used to provide positional constraints for feature pooling, most related works attempted to make each query in DETR more explicitly related to a specific spatial position rather than multiple position modes in the vanilla DETR. For example, Deformable DETR (Zhu et al., 2021) directly treats 2D reference points as queries and predicts deformable sampling points for each reference point to perform deformable cross-attention operation. Conditional DETR (Meng et al., 2021) decouples the attention formulation and generates positional queries based on reference coordinates. Efficient DETR (Yao et al., 2021) introduces a dense prediction module to select top-K positions as object queries. Although these works connect queries with positional information, they do not have an explicit formulation to use anchors.

Different from the hypothesis in prior works that the learnable query vectors contain box coordinate information, our approach is based on a new perspective that all information contained in queries are box coordinates. That is, anchor boxes are better queries for DETR. A concurrent work Anchor DETR (Wang et al., 2021) also suggests learning anchor points directly, while it ignores the anchor width and height information as in other prior works. Besides DETR, Sun et al. (2021) proposed a sparse detector by learning boxes directly, which shares a similar anchor formulation with us, but it discards the Transformer structure and leverages hard ROI align for feature extraction. Table 1 summarizes the key differences between related works and our proposed DAB-DETR. We compare our model with related works on five dimensions: if the model directly learns anchors, if the model predicts reference coordinates (in its intermediate stage), if the model updates the reference anchors layer-by-layer, if the model uses the standard dense cross-attention, if the attention is modulated to better match with objects of different scales, and if the model updates the learned queries layer-by-layer. A more detailed comparison of DETR-like models is available in Sec. B of Appendix. We recommend this section for readers who have confusions about the table.

Table 1: Comparison of representative related models and our DAB-DETR. The term "Learn Anchors?" asks if the model learns 2D points or 4D anchors as learnable parameters directly. The term "Reference Anchors" means if the model predicts relative coordinates with respect to a reference points/anchors. The term "Dynamic Anchors" indicates if the model updates its anchors layer-by-layer. The term "Standard Attention" shows whether the model leverages the standard dense attention in cross-attention modules. The term "Object Scale-Modulated Attention" means if the attention is modulated to better match with object scales. The term "Size-Modulated Attention" means if the attention is modulated to better match with object scales. The term "Update Spatial Learned Queries?" means if the learned queries are updated layer by layer. Note that Sparse RCNN is not a DETR-like architecture. We list it here for their similar anchor formulation with us. See Sec. B of Appendix for a more detailed comparison of these models.  

<table><tr><td>Models</td><td>Learn Anchors?</td><td>Reference Anchors</td><td>Dynamic Anchors</td><td>Standard Attention</td><td>Size-Modulated Attention</td><td>Update Learned Spatial Queries?</td></tr><tr><td>DETR</td><td>No</td><td>No</td><td></td><td>✓</td><td></td><td></td></tr><tr><td>Deformable DETR</td><td>No</td><td>4D</td><td>✓</td><td></td><td>✓</td><td></td></tr><tr><td>SMCA</td><td>No</td><td>4D</td><td></td><td>✓</td><td>✓</td><td></td></tr><tr><td>Conditional DETR</td><td>No</td><td>2D</td><td></td><td>✓</td><td></td><td></td></tr><tr><td>Anchor DETR</td><td>2D</td><td>2D</td><td>✓</td><td></td><td></td><td></td></tr><tr><td>Sparse RCNN</td><td>4D</td><td>4D</td><td>✓</td><td></td><td></td><td></td></tr><tr><td>DAB-DETR</td><td>4D</td><td>4D</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td></tr></table>

# 3 WHY A POSITIONAL PRIOR COULD SPEEDUP TRAINING?

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/fcda8b8975c8239bc58c4404336f0027b9e94e26ff0dce369f93fa3279f85d64.jpg)  
(a) Self-attention in encoder of DETR

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/e3bd9670183b2aa4f45255285c1e93eb59b6087c24091c3e830da16d6de17dd9.jpg)  
Figure 2: Comparison of self-attention in encoders and cross-attention in decoders of DETR. As they have the same key and value components, the only difference comes from the queries. Each query in an encoder is composed of an image feature (content information) and a positional embedding (positional information), whereas each query in a decoder is composed of a decoder embedding (content information) and a learnable query (positional information). The differences between two modules are marked in purple.  
(b) Cross-attention in decoder of DETR

Much work has been done to accelerate the training convergence speed of DETR, while lacking a unified understanding of why their methods work. Sun et al. (2020) showed that the cross-attention module is mainly responsible for the slow convergence, but they simply removed the decoders for faster training. We follow their analysis to find which sub-module in the cross-attention affects the performance. Comparing the self-attention module in encoders with the cross-attention module in decoders, we find the key difference between their inputs comes from the queries, as shown in Fig. 2. As the decoder embeddings are initialized as 0, they are projected to the same space as the image features after the first cross-attention module. After that, they will go through a similar process in decoder layers as the image features in encoder layers. Hence the root cause is likely due to the learnable queries.

Two possible reasons in cross-attention account for the model's slow training convergence: 1) it is hard to learn the queries due to the optimization challenge, and 2) the positional information in the learned queries is not encoded in the same way as the sinusoidal positional encoding used for image features. To see if it is the first reason, we reuse the well-learned queries from DETR (keep them fixed) and only train the other modules. The training curves in Fig. 3(a) show that the fixed queries only slightly improve the convergence in very early epochs, e.g. the first 25 epochs. Hence the query learning (or optimization) is likely not the key concern.

Then we turn to the second possibility and try to find out if the learned queries have some undesirable properties. As the learned queries are used to filter objects in certain regions, we visualize a few positional attention maps between the learned queries and the positional embeddings of image

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/f291143bdb84a41cd1f5f25ec8363eb4888f01837bef351241b441d2562b4424.jpg)  
(a)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/e647e42bb36e071553d2b72d029771efe1644d242cc5c022aea315640a28ca9c.jpg)  
Figure 3: a): Training curves of the original DETR and DETR with fixed queries. b): Training curves of the original DETR and DETR+DAB. We run each experiment 3 times and plot the mean value and the  $95\%$  confidence interval of each item.

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/715c420c892afde83b3272d451b9c2b3cd143ecc5955a9d9b7987ece23822e28.jpg)  
(b)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/dfb78cf7042f5006851dd87d7a9dd95085c84d9c3ab8a34ba0c1276824322c52.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/931e566003b51acc5b10365b78436cb61b0d0b09fc68557cecad6dc50670dbff.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/e07bfc0463701d76d7b918a143072045ca07aac1a04439cc0ed92689ddcdd195.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/ab4c374cb4cd04acf1bb7096932e7174a837f8f752785a23aebe8a641e2b0fb4.jpg)  
(a) DETR

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/13211df8a43ddac2070517b6de7c8fb8776aec27afc03d43de5dc2ba20415e57.jpg)  
Figure 4: We visualize the positional attention between positional queries and positional keys for DETR, Conditional DETR, and our proposed DAB-DETR. Four attention maps in (a) are randomly sampled, and we select figures with similar query positions as in (a) for (b) and (c). The darker the color, the greater the attention weight, and vice versa. (a) Each attention map in DETR is calculated by performing dot product between a learned query and positional embeddings from a feature map, and can have multiple modes and unconcentrated attentions. (b) The positional queries in Conditional DETR are encoded in the same way as the image positional embeddings, resulting in Gaussian-like attention maps. However, it cannot adapt to objects of different scales. (c) DAB-DETR explicitly modulates the attention map using the width and height information of an anchor, making it more adaptive to object size and shape. The modulated attentions can be regarded as helping perform soft ROI pooling.

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/9325a7c11b41aefa993520f95163261abfaaa40306188d14bf87ff5ab323e1d1.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/ecfb092fac8ce44936bea4e58c49d0faaa8ae47dcdd8fd51e63d051a0356cfc2.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/f0a800ea4eb9b7fe7def897a8200ded2c6b89d3d3db6489d93a94ca61a2bed32.jpg)  
(b) Conditional DETR

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/310f32019157804b20a8df09e06ea863e2496f5e2a2ac64677a7e3a65bf0f45f.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/233ff47945804ec91dad957544edc2a454d043ecd492c5f673a40fce552aacf7.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/a66c2a979fea184a66e2bf57df188e5ada737381c23397325f90bae346a68dce.jpg)  
(c) DAB-DETR

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/127dcedbe0f971b587fcf45067d48a161ace0b77c7655155ed5fa488e42ac9e2.jpg)

features in Fig. 4(a). Each query can be regarded as a positional prior to let decoders focus on a region of interest. Although they serve as a positional constraint, they also carry undesirable properties: multiple modes and nearly uniform attention weights. For example, the two attention maps at the top of Fig. 4(a) have two or more concentration centers, making it hard to locate objects when multiple objects exist in an image. The bottom maps of Fig. 4(a) focus on areas that are either too large or too small, and hence cannot inject useful positional information into the procedure of feature extraction. We conjecture that the multiple mode property of queries in DETR is likely the root cause for its slow training and we believe introducing explicit positional priors to constrain queries on a local region is desirable for training. To verify this assumption, we replace the query formulation in DETR with dynamic anchor boxes, which can enforce each query to focus on a specific area, and name this model  $\mathrm{DETR + DAB}$ . The training curves in Fig. 3(b) show that  $\mathrm{DETR + DAB}$  leads to a much better performance compared with DETR, in terms of both detection AP and training/testing loss. Note that the only difference between DETR and  $\mathrm{DETR + DAB}$  is the formulation of queries and no other techniques like 300 queries or focal loss are introduced. It shows that after addressing the multi-mode issue of DETR queries, we can achieve both a faster training convergence and a higher detection accuracy.

Some previous works also have similar analysis and confirmed this. For example, SMCA (Gao et al., 2021) speeds up the training by applying pre-defined Gaussian maps around reference points. Conditional DETR (Meng et al., 2021) uses explicit positional embedding as positional queries for training, yielding attention maps similar to Gaussian kernels as shown in Fig. 4(b). Although explicit positional priors lead to good performance in training, they ignore the scale information of an object. In contrast, our proposed DAB-DETR explicitly takes into account the object scale information to adaptively adjust attention weights, as shown in Fig. 4(c).

# 4 DAB-DETR

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/6398f061f8d921d68aca9d661c4bff2021bde0b06254d6abd6c4950c968e93a5.jpg)  
Figure 5: Framework of our proposed DAB-DETR.

# 4.1 OVERVIEW

Following DETR (Carion et al., 2020), our model is an end-to-end object detector which includes a CNN backbone, Transformer (Vaswani et al., 2017) encoders and decoders, and prediction heads for boxes and labels. We mainly improve the decoder part, as shown in Fig. 5.

Given an image, we extract image spatial features using a CNN backbone followed with Transformer encoders to refine the CNN features. Then dual queries, including positional queries (anchor boxes) and content queries (decoder embeddings), are fed into the decoder to probe the objects which correspond to the anchors and have similar patterns with the content queries. The dual queries are updated layer-by-layer to get close to the target ground-truth objects gradually. The outputs of the final decoder layer are used to predict the objects with labels and boxes by prediction heads, and then a bipartite graph matching is conducted to calculate loss as in DETR.

To illustrate the generality of our dynamic anchor boxes, we also design a stronger DAB-Deformable-DETR, which is available in Appendix.

# 4.2 LEARNING ANCHOR BOXES DIRECTLY

As discussed in Sec. 1 regarding the role of queries in DETR, we propose to directly learn query boxes or say anchor boxes and derive positional queries from these anchors. There are two attention modules in each decoder layer, including a self-attention module and a cross-attention module, which are used for query updating and feature probing respectively. Each module needs queries, keys, and values to perform attention-based value aggregation, yet the inputs of these triplets differ.

We denote  $A_{q} = (x_{q},y_{q},w_{q},h_{q})$  as the  $q$ -th anchor,  $x_{q},y_{q},w_{q},h_{q}\in \mathbb{R}$ , and  $C_q\in \mathbb{R}^D$  and  $P_{q}\in \mathbb{R}^{D}$  as its corresponding content query and positional query, where  $D$  is the dimension of decoder embeddings and positional queries.

Given an anchor  $A_{q}$ , its positional query  $P_{q}$  is generated by:

$$
P _ {q} = \operatorname {M L P} \left(\operatorname {P E} \left(A _ {q}\right)\right), \tag {1}
$$

where PE means positional encoding to generate sinusoidal embeddings from float numbers and the parameters of MLP are shared across all layers. As  $A_{q}$  is a quaternion, we overload the PE operator here:

$$
\mathrm {P E} \left(A _ {q}\right) = \mathrm {P E} \left(x _ {q}, y _ {q}, w _ {q}, h _ {q}\right) = \operatorname {C a t} \left(\mathrm {P E} \left(x _ {q}\right), \mathrm {P E} \left(y _ {q}\right), \mathrm {P E} \left(w _ {q}\right), \mathrm {P E} \left(h _ {q}\right)\right). \tag {2}
$$

The notion Cat means concatenation function. In our implementations, the positional encoding function PE maps a float to a vector with  $D / 2$  dimensions as: PE:  $\mathbb{R} \to \mathbb{R}^{D / 2}$ . Hence the function MLP projects a  $2D$  dimensional vector into  $D$  dimensions: MLP:  $\mathbb{R}^{2D} \to \mathbb{R}^D$ . The MLP module has two submodules, each of which is composed of a linear layer and a ReLU activation, and the feature reduction is conducted at the first linear layer.

In the self-attention module, all three of queries, keys, and values have the same content items, while the queries and keys contain extra position items:

$$
\text {S e l f - A t t n :} \quad Q _ {q} = C _ {q} + P _ {q}, \quad K _ {q} = C _ {q} + P _ {q}, \quad V _ {q} = C _ {q}, \tag {3}
$$

Inspired by Conditional DETR (Meng et al., 2021), we concatenate the position and content information together as queries and keys in the cross-attention module, so that we can decouple the content and position contributions to the query-to-feature similarity computed as the dot product between a query and a key. To rescale the positional embeddings, we leverage the conditional spatial query (Meng et al., 2021) as well. More specifically, we learn a  $\mathrm{MLP}^{(\mathrm{csq})}: \mathbb{R}^D \to \mathbb{R}^D$  to obtain a scale vector conditional on the content information and use it to perform element-wise multiplication with the positional embeddings:

$$
\text {C r o s s - A t t n :} \quad Q _ {q} = \operatorname {C a t} \left(C _ {q}, \operatorname {P E} \left(x _ {q}, y _ {q}\right) \cdot \operatorname {M L P} ^ {\left(\mathrm {c s q}\right)} \left(C _ {q}\right)\right),
$$

$$
K _ {x, y} = \operatorname {C a t} \left(F _ {x, y}, \operatorname {P E} (x, y)\right), \quad V _ {x, y} = F _ {x, y}, \tag {4}
$$

where  $F_{x,y} \in \mathbb{R}^D$  is the image feature at position  $(x,y)$  and  $\cdot$  is an element-wise multiplication. Both the positional embeddings in queries and keys are generated based on 2D coordinates, making it more consistent to compare the positional similarity, as in previous works (Meng et al., 2021; Wang et al., 2021).

# 4.3 ANCHOR UPDATE

Using coordinates as queries for learning makes it possible to update them layer-by-layer. In contrast, for queries of high dimensional embeddings, such as in DETR (Carion et al., 2020) and Conditional DETR (Meng et al., 2021), it is hard to perform layer-by-layer query refinement, because it is unclear how to convert an updated anchor back to a high-dimensional query embedding.

Following the previous practice (Zhu et al., 2021; Wang et al., 2021), we update anchors in each layer after predicting relative positions  $(\Delta x, \Delta y, \Delta w, \Delta h)$  by a prediction head, as shown in Fig. 5. Note that all prediction heads in different layers share the same parameters.

# 4.4 WIDTH & HEIGHT-MODULATED GAUSSIAN KERNEL

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/c23bce1df580884d0b05643a1a4679104ef0d48877e405b4b56fd694bb0c374e.jpg)  
$\mathrm{H} = 1$ $\mathrm{W} = 1$

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/5751c48c7ce3af2537aba2f93e34e7fee8cc164fec2bdd80641fa4047106d27f.jpg)  
Figure 6: Positional attention maps modulated by width and height.  
$\mathrm{H} = 1,\mathrm{W} = 3$

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/5e03af4e66ca3e6b18b60bd2714d74dac87e9b4bd65ee8fbb53c201caf8a4aa3.jpg)  
$\mathrm{H} = 3$ $\mathrm{W} = 1$

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/18616f2d0560985af151bc7b0428c04364e5cb273037c406cf91852746770df4.jpg)  
Figure 7: Positional attention maps with different temperatures.  
Temperature=1

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/05dd505e33bb13200832014c5e98e0011b944b414d5140a8c229a4731ccdf29d.jpg)  
Temperature=10

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/0d54de07395f5222c5bfd7d40c0a7e0805b5d4ef58a0f76a038a08fe38de79b2.jpg)  
Temperature=10000

Traditional positional attention maps are used as a Gaussian-like prior, as shown in Fig. 6 left. But the prior is simply assumed isotropic and fixed size for all objects, leaving their scale information

(width and height) ignored. To improve the positional prior, we propose to inject the scale information into the attention maps.

The query-to-key similarity in the original positional attention map is computed as the sum of dot products of two coordinate encodings:

$$
\operatorname {A t t n} ((x, y), (x _ {\text {r e f}}, y _ {\text {r e f}})) = (\mathrm {P E} (x) \cdot \mathrm {P E} (x _ {\text {r e f}}) + \mathrm {P E} (y) \cdot \mathrm {P E} (y _ {\text {r e f}})) / \sqrt {D}, \tag {5}
$$

where  $1 / \sqrt{D}$  is used to rescale the value as suggested in Vaswani et al. (2017). We modulate the positional attention maps (before softmax) by dividing the relative anchor width and height from its  $x$  part and  $y$  part separately to smooth the Gaussian prior to better match with objects of different scales:

$$
\text {M o d u l a t e A t t n} ((x, y), (x _ {\text {r e f}}, y _ {\text {r e f}})) = (\mathrm {P E} (x) \cdot \mathrm {P E} (x _ {\text {r e f}}) \frac {w _ {q , \text {r e f}}}{w _ {q}} + \mathrm {P E} (y) \cdot \mathrm {P E} (y _ {\text {r e f}}) \frac {h _ {q , \text {r e f}}}{h _ {q}}) / \sqrt {D}, \tag {6}
$$

where  $w_{q}$  and  $h_{q}$  are the width and height of the anchor  $A_{q}$ , and  $w_{q,\mathrm{ref}}$  and  $h_{q,\mathrm{ref}}$  are the reference width and height that are calculated by:

$$
w _ {q, \text {r e f}}, h _ {q, \text {r e f}} = \sigma \left(\operatorname {M L P} \left(C _ {q}\right)\right). \tag {7}
$$

This modulated positional attention helps us extract features of objects with different widths and heights, and the visualizations of modulated attentions are shown in Fig. 6.

# 4.5 TEMPERATURETUNING

For position encoding, we use the sinusoidal function (Vaswani et al., 2017), which is defined as:

$$
\mathrm {P E} (x) _ {2 i} = \sin \left(\frac {x}{T ^ {2 i / D}}\right), \quad \mathrm {P E} (x) _ {2 i + 1} = \cos \left(\frac {x}{T ^ {2 i / D}}\right), \tag {8}
$$

where  $T$  is a hand-design temperature, and the superscript  $2i$  and  $2i + 1$  denote the indices in the encoded vectors. The temperature  $T$  in Eq. (8) influences the size of positional priors, as shown in Fig. 7. A larger  $T$  results in a more flattened attention map, and vice versa. Note that the temperature  $T$  is hard-coded in (Vaswani et al., 2017) as 10000 for nature language processing, in which the values of  $x$  are integers representing each word's position in a sentence. However, in DETR, the values of  $x$  are floats between 0 and 1 representing bounding box coordinates. Hence a different temperature is highly desired for vision tasks. In this work, we empirically choose  $T = 20$  in all our models.

# 5 EXPERIMENTS

We provide the training details in Appendix A.

# 5.1 MAIN RESULTS

Table 2 shows our main results on the COCO 2017 validation set. We compare our proposed DAB-DETR with DETR (Carion et al., 2020), Faster RCNN (Ren et al., 2017), Anchor DETR (Wang et al., 2021), SMCA (Gao et al., 2021), Deformable DETR (Zhu et al., 2021), TSP (Sun et al., 2020), and Conditional DETR (Meng et al., 2021). We showed two variations of our model: standard models and models marked with superscript * that have 3 pattern embeddings (Wang et al., 2021). Our standard models outperform Conditional DETR with a large margin. We notice that our model introduces a slight increase of GFLOPs. GFLOPs may differ depending on the calculation scripts and we use the results reported by the authors in Table 2. Actually, we find in our tests that the GFLOPs of our standatd models are nearly the same as the corresponding Conditional DETR models based on our GFLOPs calculation scripts, hence our model still has advantages over previous work under the same settings. When using pattern embeddings, our DAB-DETR with * outperforms previous DETR-like methods on all four backbones with a large margin, even better than multiscale architectures. It verifies the correctness of our analysis and the effectiveness of our design.

Table 2: Results for our DAB-DETR and other detection models. All DETR-like models except DETR use 300 queries, while DETR uses 100. The models with superscript * use 3 pattern embeddings as in Anchor DETR (Wang et al., 2021). We also provide stronger results of our DAB-DETR in Appendix G and Appendix C.  

<table><tr><td>Model</td><td>MultiScale</td><td>#epochs</td><td>AP</td><td>\( AP_{50} \)</td><td>\( AP_{75} \)</td><td>\( AP_S \)</td><td>\( AP_M \)</td><td>\( AP_L \)</td><td>GFLOPs</td><td>Params</td></tr><tr><td>DETR-R50</td><td></td><td>500</td><td>42.0</td><td>62.4</td><td>44.2</td><td>20.5</td><td>45.8</td><td>61.1</td><td>86</td><td>41M</td></tr><tr><td>Faster RCNN-FPN-R50</td><td></td><td>108</td><td>42.0</td><td>62.1</td><td>45.5</td><td>26.6</td><td>45.5</td><td>53.4</td><td>180</td><td>42M</td></tr><tr><td>Anchor DETR-R50*</td><td></td><td>50</td><td>42.1</td><td>63.1</td><td>44.9</td><td>22.3</td><td>46.2</td><td>60.0</td><td>-</td><td>39M</td></tr><tr><td>Conditional DETR-R50</td><td></td><td>50</td><td>40.9</td><td>61.8</td><td>43.3</td><td>20.8</td><td>44.6</td><td>59.2</td><td>90</td><td>44M</td></tr><tr><td>DAB-DETR-R50</td><td></td><td>50</td><td>42.2</td><td>63.1</td><td>44.7</td><td>21.5</td><td>45.7</td><td>60.3</td><td>94</td><td>44M</td></tr><tr><td>DAB-DETR-R50*</td><td></td><td>50</td><td>42.6</td><td>63.2</td><td>45.6</td><td>21.8</td><td>46.2</td><td>61.1</td><td>100</td><td>44M</td></tr><tr><td>DETR-DC5-R50</td><td></td><td>500</td><td>43.3</td><td>63.1</td><td>45.9</td><td>22.5</td><td>47.3</td><td>61.1</td><td>187</td><td>41M</td></tr><tr><td>Deformable DETR-R50</td><td>✓</td><td>50</td><td>43.8</td><td>62.6</td><td>47.7</td><td>26.4</td><td>47.1</td><td>58.0</td><td>173</td><td>40M</td></tr><tr><td>SMCA-R50</td><td>✓</td><td>50</td><td>43.7</td><td>63.6</td><td>47.2</td><td>24.2</td><td>47.0</td><td>60.4</td><td>152</td><td>40M</td></tr><tr><td>TSP-RCNN-R50</td><td>✓</td><td>96</td><td>45.0</td><td>64.5</td><td>49.6</td><td>29.7</td><td>47.7</td><td>58.0</td><td>188</td><td>-</td></tr><tr><td>Anchor DETR-DC5-R50*</td><td></td><td>50</td><td>44.2</td><td>64.7</td><td>47.5</td><td>24.7</td><td>48.2</td><td>60.6</td><td>151</td><td>39M</td></tr><tr><td>Conditional DETR-DC5-R50</td><td></td><td>50</td><td>43.8</td><td>64.4</td><td>46.7</td><td>24.0</td><td>47.6</td><td>60.7</td><td>195</td><td>44M</td></tr><tr><td>DAB-DETR-DC5-R50</td><td></td><td>50</td><td>44.5</td><td>65.1</td><td>47.7</td><td>25.3</td><td>48.2</td><td>62.3</td><td>202</td><td>44M</td></tr><tr><td>DAB-DETR-DC5-R50*</td><td></td><td>50</td><td>45.7</td><td>66.2</td><td>49.0</td><td>26.1</td><td>49.4</td><td>63.1</td><td>216</td><td>44M</td></tr><tr><td>DETR-R101</td><td></td><td>500</td><td>43.5</td><td>63.8</td><td>46.4</td><td>21.9</td><td>48.0</td><td>61.8</td><td>152</td><td>60M</td></tr><tr><td>Faster RCNN-FPN-R101</td><td></td><td>108</td><td>44.0</td><td>63.9</td><td>47.8</td><td>27.2</td><td>48.1</td><td>56.0</td><td>246</td><td>60M</td></tr><tr><td>Anchor DETR-R101*</td><td></td><td>50</td><td>43.5</td><td>64.3</td><td>46.6</td><td>23.2</td><td>47.7</td><td>61.4</td><td>-</td><td>58M</td></tr><tr><td>Conditional DETR-R101</td><td></td><td>50</td><td>42.8</td><td>63.7</td><td>46.0</td><td>21.7</td><td>46.6</td><td>60.9</td><td>156</td><td>63M</td></tr><tr><td>DAB-DETR-R101</td><td></td><td>50</td><td>43.5</td><td>63.9</td><td>46.6</td><td>23.6</td><td>47.3</td><td>61.5</td><td>174</td><td>63M</td></tr><tr><td>DAB-DETR-R101*</td><td></td><td>50</td><td>44.1</td><td>64.7</td><td>47.2</td><td>24.1</td><td>48.2</td><td>62.9</td><td>179</td><td>63M</td></tr><tr><td>DETR-DC5-R101</td><td></td><td>500</td><td>44.9</td><td>64.7</td><td>47.7</td><td>23.7</td><td>49.5</td><td>62.3</td><td>253</td><td>60M</td></tr><tr><td>TSP-RCNN-R101</td><td>✓</td><td>96</td><td>46.5</td><td>66.0</td><td>51.2</td><td>29.9</td><td>49.7</td><td>59.2</td><td>254</td><td>-</td></tr><tr><td>SMCA-R101</td><td>✓</td><td>50</td><td>44.4</td><td>65.2</td><td>48.0</td><td>24.3</td><td>48.5</td><td>61.0</td><td>218</td><td>50M</td></tr><tr><td>Anchor DETR-R101*</td><td></td><td>50</td><td>45.1</td><td>65.7</td><td>48.8</td><td>25.8</td><td>49.4</td><td>61.6</td><td>-</td><td>58M</td></tr><tr><td>Conditional DETR-DC5-R101</td><td></td><td>50</td><td>45.0</td><td>65.5</td><td>48.4</td><td>26.1</td><td>48.9</td><td>62.8</td><td>262</td><td>63M</td></tr><tr><td>DAB-DETR-DC5-R101</td><td></td><td>50</td><td>45.8</td><td>65.9</td><td>49.3</td><td>27.0</td><td>49.8</td><td>63.8</td><td>282</td><td>63M</td></tr><tr><td>DAB-DETR-DC5-R101*</td><td></td><td>50</td><td>46.6</td><td>67.0</td><td>50.2</td><td>28.1</td><td>50.5</td><td>64.1</td><td>296</td><td>63M</td></tr></table>

Table 3: Ablation results for our DAB-DETR. All models are tested over ResNet-50-DC5 backbone and the other parameters are the same as our default settings.  

<table><tr><td>#Row</td><td>Anchor Box (4D) vs. Point (2D)</td><td>Anchor Update</td><td>wh-Modulated Attention</td><td>Temperature Tuning</td><td>AP</td></tr><tr><td>1</td><td>4D</td><td>✓</td><td>✓</td><td>✓</td><td>45.7</td></tr><tr><td>2</td><td>4D</td><td></td><td>✓</td><td>✓</td><td>44.0</td></tr><tr><td>3</td><td>4D</td><td>✓</td><td></td><td>✓</td><td>45.0</td></tr><tr><td>4</td><td>2D</td><td>✓</td><td></td><td>✓</td><td>44.0</td></tr><tr><td>5</td><td>4D</td><td>✓</td><td>✓</td><td></td><td>44.4</td></tr></table>

# 5.2 ABLATIONS

Table 3 shows the effectiveness of each component in our model. We find that all modules we proposed contribute remarkably to our final results. The anchor box formulation improves the performance from  $44.0\%$  AP to  $45.0\%$  AP compared with anchor point formulation (compare Row 3 and Row 4) and anchor update introduces  $1.7\%$  AP improvement (compare Row 1 and Row 2), which demonstrates the effectiveness of dynamic anchor box design.

After removing modulated attention and temperature tuning, the model performance drops to  $45.0\%$  (compare Row 1 and Row 3) and  $44.4\%$  (compare Row 1 and Row 5), respectively. Hence fine-grained tuning of positional attentions is of great importance for improving the detection performance as well.

# 6 CONCLUSION

We have presented in this paper a novel query formulation using dynamic anchor boxes for DETR and offer a deeper understanding of the role of queries in DETR. Using anchor boxes as queries lead to several advantages, including a better positional prior with temperature tuning, size-modulated

attention to account for objects of different scales, and iterative anchor update for improving anchor estimate gradually. Such a design makes it clear that queries in DETR can be implemented as performing soft ROI pooling layer-by-layer in a cascade manner. Extensive experiments were conducted and effectively confirmed our analysis and verified our algorithm design.

# ACKNOWLEDGEMENTS

This work was supported by the National Key Research and Development Program of China (2020AAA0104304, 2020AAA0106000, 2020AAA0106302), NSFC Projects (Nos. 61620106010, 62061136001, 61621136008, 62076147, U19B2034, U1811461, U19A2081), Beijing NSF Project (No. JQ19016), Beijing Academy of Artificial Intelligence (BAAI), Tsinghua-Alibaba Joint Research Program, Tsinghua Institute for Guo Qiang, Tsinghua-OPPO Joint Research Center for Future Terminal Technology.

# ETHICS STATEMENT

Object detection is a fundamental task in computer vision with wide applications. Hence any improvement of this field will yield lots of impacts. To visually perceive and interact with the environment, autonomous vehicles highly depend on this technique and will benefit from any of its improvement. It has also led to advances in medical imaging, word recognition, instance segmentation on natural images, and so on. Therefore a failure in this model could affect many tasks. Our study provides a deeper understanding of the roles of queries in DETR and improves the interpretability of this important submodule in the end-to-end Transformer-based detection framework.

As our model relies on deep neural networks, it can be attacked by adversarial examples. Similarly, as it relies on training data, it may produce biased results induced from training samples. These are common problems in deep learning and our community is working together to improve them. Finally, it is worth noting that detection models, especially face or human detection models, might pose a threat to people's privacy and security if used by someone up to no good.

# REPRODUCIBILITY STATEMENT

We confirm the reproducibility of the results. All materials that are needed to reproduce our results will be released after blind review. We will open source the code as well.

# REFERENCES

Alexey Bochkovskiy, Chien-Yao Wang, and Hong-Yuan Mark Liao. Yolov4: Optimal speed and accuracy of object detection. arXiv preprint arXiv:2004.10934, 2020.  
Nicolas Carion, Francisco Massa, Gabriel Synnaeve, Nicolas Usunier, Alexander Kirillov, and Sergey Zagoruyko. End-to-end object detection with transformers. In European Conference on Computer Vision, pp. 213-229. Springer, 2020.  
Xiyang Dai, Yinpeng Chen, Jianwei Yang, Pengchuan Zhang, Lu Yuan, and Lei Zhang. Dynamic detr: End-to-end object detection with dynamic attention. In Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV), pp. 2988-2997, October 2021.  
Peng Gao, Minghang Zheng, Xiaogang Wang, Jifeng Dai, and Hongsheng Li. Fast convergence of detr with spatially modulated co-attention. arXiv preprint arXiv:2101.07448, 2021.  
Zheng Ge, Songtao Liu, Feng Wang, Zeming Li, and Jian Sun. Yolox: Exceeding yolo series in 2021. arXiv preprint arXiv:2107.08430, 2021.  
Ross Girshick. Fast r-cnn. In 2015 IEEE International Conference on Computer Vision (ICCV), pp. 1440-1448, 2015.  
Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Delving deep into rectifiers: Surpassing human-level performance on imagenet classification. In 2015 IEEE International Conference on Computer Vision (ICCV), pp. 1026-1034, 2015.

Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Deep residual learning for image recognition. In 2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR), pp. 770-778, 2016.  
Tsung-Yi Lin, Michael Maire, Serge Belongie, James Hays, Pietro Perona, Deva Ramanan, Piotr Dólar, and C Lawrence Zitnick. Microsoft coco: Common objects in context. In European conference on computer vision, pp. 740-755. Springer, 2014.  
Tsung-Yi Lin, Priya Goyal, Ross Girshick, Kaiming He, and Piotr Dollar. Focal loss for dense object detection. IEEE Transactions on Pattern Analysis and Machine Intelligence, 42(2):318-327, 2020.  
Ilya Loshchilov and Frank Hutter. Decoupled weight decay regularization. In International Conference on Learning Representations, 2018.  
Depu Meng, Xiaokang Chen, Zejia Fan, Gang Zeng, Houqiang Li, Yuhui Yuan, Lei Sun, and Jingdong Wang. Conditional detr for fast training convergence. arXiv preprint arXiv:2108.06152, 2021.  
Joseph Redmon, Santosh Divvala, Ross Girshick, and Ali Farhadi. You only look once: Unified, real-time object detection. In 2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR), pp. 779-788, 2016.  
Shaoqing Ren, Kaiming He, Ross Girshick, and Jian Sun. Faster r-cnn: Towards real-time object detection with region proposal networks. IEEE Transactions on Pattern Analysis and Machine Intelligence, 39(6):1137-1149, 2017.  
Hamid Rezatofighi, Nathan Tsoi, JunYoung Gwak, Amir Sadeghian, Ian Reid, and Silvio Savarese. Generalized intersection over union: A metric and a loss for bounding box regression. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 658-666, 2019.  
Peize Sun, Rufeng Zhang, Yi Jiang, Tao Kong, Chenfeng Xu, Wei Zhan, Masayoshi Tomizuka, Lei Li, Zehuan Yuan, Changhu Wang, and Ping Luo. Sparse r-cnn: End-to-end object detection with learnable proposals. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 14454-14463, 2021.  
Zhiqing Sun, Shengcao Cao, Yiming Yang, and Kris Kitani. Rethinking transformer-based set prediction for object detection. arXiv preprint arXiv:2011.10881, 2020.  
Zhi Tian, Chunhua Shen, Hao Chen, and Tong He. Fcos: Fully convolutional one-stage object detection. In 2019 IEEE/CVF International Conference on Computer Vision (ICCV), pp. 9627-9636, 2019.  
Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N Gomez, Lukasz Kaiser, and Illia Polosukhin. Attention is all you need. In Advances in neural information processing systems, pp. 5998-6008, 2017.  
Yingming Wang, Xiangyu Zhang, Tong Yang, and Jian Sun. Anchor detr: Query design for transformer-based detector. arXiv preprint arXiv:2109.07107, 2021.  
Zhuyu Yao, Jiangbo Ai, Boxun Li, and Chi Zhang. Efficient detr: Improving end-to-end object detector with dense prior. arXiv preprint arXiv:2104.01318, 2021.  
Xingyi Zhou, Dequan Wang, and Philipp Krahenbuhl. Objects as points. arXiv preprint arXiv:1904.07850, 2019.  
Xizhou Zhu, Weijie Su, Lewei Lu, Bin Li, Xiaogang Wang, and Jifeng Dai. Deformable detr: Deformable transformers for end-to-end object detection. In ICLR 2021: The Ninth International Conference on Learning Representations, 2021.

# Appendix for DAB-DETR

# A TRAINING DETAILS

Architecture. Our model is almost the same as DETR which includes a CNN backbone, multiple Transformer (Vaswani et al., 2017) encoders and decoders, and two prediction heads for boxes and labels. We use ImageNet-pretrained ResNet (He et al., 2016) as our backbones, and 6 Transformer encoders and 6 Transformer decoders in our implementations. We follow previous works to report results over four backbones: ResNet-50, ResNet-101, and their  $16\times$  -resolution extensions ResNet50-DC5 and ResNet-101-DC5. As we need to predict boxes and labels in each decoder layer, the MLP networks for box and label predictions share the same parameters across different decoder layers. As inspired by Anchor DETR, we also leverage multiple pattern embeddings to perform multiple predictions at one position and the number of patterns is set as 3 which is the same as Anchor DETR. We also leverage PReLU (He et al., 2015) as our activations.

Following Deformable DETR and Conditional DETR, we use 300 anchors as queries. We select 300 predicted boxes and labels with the largest classification logits for evaluation as well. We also use focal loss (Lin et al., 2020) with  $\alpha = 0.25$ ,  $\gamma = 2$  for classification. The same loss terms are used in bipartite matching and final loss calculating, but with different coefficients. Classification loss with coefficient 2.0 is used in bipartite matching but 1.0 in the final loss. L1 loss with coefficient 5.0 and GIOU loss (Rezatofighi et al., 2019) with coefficient 2.0 are consistent in both the matching and the final loss calculation procedures. All models are trained on 16 GPUs with 1 image per GPU and AdamW (Loshchilov & Hutter, 2018) is used for training with weight decay  $10^{-4}$ . The learning rates for backbone and other modules are set to  $10^{-5}$  and  $10^{-4}$  respectively. We train our models for 50 epochs and drop the learning rate by 0.1 after 40 epochs. All models are trained on Nvidia A100 GPU. We search hyperparameters with batch size 64 and all results in our paper are reported with batch size 16. For better reproducing our results, we provide the memory needed and batch size/GPU in Table 4.

Dataset. We conduct the experiments on the COCO (Lin et al., 2014) object detection dataset. All models are trained on the train2017 split and evaluated on the val2017 split.

Table 4: GPU memory usage of each model.  

<table><tr><td>Model</td><td>Batch Size/GPU</td><td>GPU Memory (MB)</td></tr><tr><td>DAB-DETR-R50</td><td>2</td><td>6527</td></tr><tr><td>DAB-DETR-R50*</td><td>1</td><td>3573</td></tr><tr><td>DAB-DETR-R50-DC5</td><td>1</td><td>13745</td></tr><tr><td>DAB-DETR-R50-DC5*</td><td>1</td><td>15475</td></tr><tr><td>DAB-DETR-R101</td><td>2</td><td>6913</td></tr><tr><td>DAB-DETR-R101*</td><td>1</td><td>4369</td></tr><tr><td>DAB-DETR-R101-DC5</td><td>1</td><td>13148</td></tr><tr><td>DAB-DETR-R101-DC5*</td><td>1</td><td>16744</td></tr></table>

# B COMPARISON OF DETR-LIKE MODELS

In this section, we provide a more detailed comparison of DETR-like models, including DETR (Carion et al., 2020), Conditional DETR (Meng et al., 2021), Anchor DETR (Wang et al., 2021), Deformable DETR (Zhu et al., 2021), our proposed DAB-DETR, and DAB-Deformable-DETR. Their model designs are illustrated in Fig. 8. We will discuss the difference between previous models and our models.

Anchor DETR (Wang et al., 2021) improves DETR by introducing 2D anchor points, which are updated layer by layer. It shares a similar motivation with our work. But it leaves the object scale information unconsidered and thus cannot modulate the cross-attention to make it adapt to objects of different scales. Moreover, the positional queries in its framework are of high dimension and passed to the self-attention modules in all layers without any adaptation. See the brown colored part in Fig. 8 (d) for details. This design might be sub-optimal as the self-attention modules cannot leverage the refined anchor points in different layers.

Deformable DETR (Zhu et al., 2021) introduces 4D anchor boxes and updates them layer by layer, which is called iterative bounding box refinement in its paper. Its algorithm is mainly developed based on deformable attention, which requires reference points to sample attention points and meanwhile utilizes box width and height to modulate attention areas. However, as iterative bounding box refinement is closely coupled with the special design of deformable attention, it is nontrivial to apply it to general Transformer decoder-based DETR models. This is probably the reason why few work after Deformable DETR adopts this idea. Moreover, the position queries in Deformable DETR are passed to both the self-attention modules and the cross-attention modules in all layers without any adaptation.

See the brown colored part in Fig. 8 (e) for details. As the result, both its self-attention modules and cross-attention modules cannot fully leverage the refined anchor boxes in different layers.

To verify our analysis, we develop a variant of Deformable-DETR by formulating its queries as dynamic anchor boxes as in DAB-DETR. We call this variant as DAB-Deformable-DETR, which is illustrated in Fig. 8 (f). Under exactly the same setting using R50 as backbone, DAB-Deformable-DETR improves Deformable-DETR by 0.5 AP (46.3 to 46.8) on COCO. See Table 5 for the performance comparison and Sec. C for more implementation details.

Dynamic DETR (Dai et al., 2021) is another interesting improvement of DETR. It also leverages anchor boxes to pool features, but it uses ROI pooling for feature extraction, which makes it less general to DETR-like models compared with our dynamic anchor boxes. Moreover, compared with cross-attention in Transformer decoders, which performs global feature pooling in a soft manner (based on attention map), the ROI pooling operation only performs local feature pooling within a ROI window. In our opinion, the ROI pooling operation can help faster convergence as it enforces each query to associate with a specific spatial position. But it may lead to sub-optimal result due to its ignorance of global context outside a ROI window.

# C DAB-DEFORMABLE-DETR

To further demonstrate the effectiveness of our dynamic anchor boxes, we develop DAB-Deformable-DETR by adding our dynamic anchor boxes design to Deformable DETR (Zhu et al., 2021) $^{2}$ . The difference between Deformable DETR and DAB-Deformable-DETR is shown in Fig. 8 (e) and (f). The results of Deformable DETR and DAB-Deformable-DETR are shown in Table 5. With no more than 10 lines of code modified, our DAB-Deformable-DETR (row 4) results in a significant performance improvement (+0.5 AP) compared with the original Deformable DETR (row 3). All other settings except the query formulation are exactly the same in this experiment.

We also compare the speed of convergence in Fig. 9. It shows that our proposed dynamic anchor boxes speed up the training as well (left in Fig. 9). We believe one of the reasons for better performance is the update of learned queries. We plot the change of total loss, which is the sum-up of losses of all decoder layers, during training in the middle figure of Fig. 9. Interestingly, it shows that the total loss of DAB-Deformable-DETR is larger than Deformable DETR. However, the loss of the final layer of DAB-Deformable-DETR is lower than that in Deformable DETR (right in Fig. 9), which is a good indicator of the better performance of DAB-Deformable-DETR as the inference result only takes from the last layer.

# D ANCHORS VISUALIZATION

We visualize the learned anchor boxes in Fig. 10. When learning anchor points as queries, the learned points are distributed evenly around the image, while the centers seem to distribute randomly when learning anchor boxes directly. This might be because the centers are coupled with anchor sizes. The right-most figure shows the visualization of the learned anchor boxes. We only show a partial set for the visualization clarity. Most boxes are of medium size and no particular pattern is found in the distribution of boxes.

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/fe8bffd1aaba489e9884777e8e48b00b37329bf12f4337781e2e8ca81b061647.jpg)  
(a) DETR

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/299d5bb81d39dc7dcb7e785e42f1d4fd2e1341e916dd57f86283e4bd55d194cb.jpg)  
(b) Conditional DETR

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/f61350fef8b4ff98c0aa8e6e1d950f2ac9629b180443fd2faa4dece0d5b5f88c.jpg)  
(c) DAB-DETR (Ours)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/2dbf1deca88104f9912b387323db1c8c44e0981bed899204d8789d24d9227fef.jpg)  
(d) Anchor-DETR

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/d6afc6009562dcbe6c5be667ed02319163c5ff90d5106acd691eafb4ccdfef3b.jpg)  
(e) Deformable DETR

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/0f9ec91e3645b6c9e74c15afb76aae2010db6449a8c34a4fc231c0b338b203a2.jpg)  
Figure 8: Comparison of DETR-like models. For clarity, we only show two layers of Transformer decoder and omit the FFN blocks. We mark the modules with difference in purple and marked the learned high-dimensional queries in brown. DAB-DETR (c) is proposed in our paper, and DAB-Deformable-DETR (f) is a variant of Deformable DETR modified by introducing our dynamic anchors boxes. All previous models (a,b,d,e) leverage high-dimensional queries (shaded in brown) to pass positional information to each layers, which are semantic ambiguous and are not updated layer by layer. In contrast, DAB-DETR (c) directly uses dynamically updated anchor boxes to provide both a reference query point  $(x,y)$  and a reference anchor size  $(w,h)$  to improve the cross-attention computation. DAB-Deformable-DETR (f) uses dynamically updated anchor boxes to formulate its queries as well.  
(f) DAB-Deformable-DETR (Ours)

Table 5: Comparison of the results of Deformable DETR and DAB-Deformable-DETR. The models in row 1 and row 2 are copied from the original paper, and the models in row 3 and row 4 are tested under the same standard R50 multi-scale setting. Deformable  $\mathrm{DETR + }$  means the Deformable DETR model with iterative bounding box refinement and the result of Deformable  $\mathrm{DETR + }$  (open source) is reported by us using the open-source code. The only difference between row 3 and row 4 is the formulation of queries.  

<table><tr><td># row</td><td>Model</td><td>AP</td><td>\( AP_{50} \)</td><td>\( AP_{75} \)</td><td>\( AP_S \)</td><td>\( AP_M \)</td><td>\( AP_L \)</td><td>Params</td></tr><tr><td>1</td><td>Deformable DETR</td><td>43.8</td><td>62.6</td><td>47.7</td><td>26.4</td><td>47.1</td><td>58.0</td><td>40M</td></tr><tr><td>2</td><td>Deformable DETR+</td><td>45.4</td><td>64.7</td><td>49.0</td><td>26.8</td><td>48.3</td><td>61.7</td><td>40M</td></tr><tr><td>3</td><td>Deformable DETR+ (open source)</td><td>46.3</td><td>65.3</td><td>50.2</td><td>28.6</td><td>49.3</td><td>62.1</td><td>47M</td></tr><tr><td>4</td><td>DAB-Deformable-DETR(Ours)</td><td>46.8</td><td>66.0</td><td>50.4</td><td>29.1</td><td>49.8</td><td>62.3</td><td>47M</td></tr></table>

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/45a83d43fb2417337522d1f4c3dc9a2542a47b690a23a9eccbe4881ec7e68093.jpg)  
Figure 9: Comparison of the training of Deformable DETR and DAB-Deformable-DETR models. We plot the change of AP (left), the loss of all layers (middle), and the loss of the last layer (right) during training, respectively. With no more than 10 lines of code modified, DAB-Deformable-DETR results in a better performance compared with the original Deformable DETR model (see the left figure). While the loss of all layers of DAB-Deformable-DETR is larger than that in Deformable DETR (see the middle figure), our models have a lower loss of the last layer (see the right figure), which is the most important as the inference result only takes from the last layer. The two models are tested under the same standard R50 multi-scale setting.

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/54196a778dbe0ccb720481dd31e614dfd6651ab7172928ecc141a3d181a13c8d.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/14c679799f9756fa6dd085253fb8630cad71a697aa158e06c76bea74c2390008.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/c114865fa159e90cd0aad13ddad52aae590aebb72a1be3a53093bf8090283898.jpg)  
Figure 10: Learned anchor points when learning 2D coordinates only (left), and anchor center points (middle) and partial anchor boxes (right) when learning anchor boxes directly.

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/035877162fc2041547999b0d517fdfdebd505ad5883870366241e3f2a2964d84.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/15d8cf8c6349bb3adc3124f659ac725fb43e307e55a3c5329c607760ba108e6e.jpg)

# E RESULTS WITH DIFFERENT TEMPERATURES

Table 6 shows the results of models using different temperatures in the positional encoding function. As larger temperature generates more flattened attention maps, it leads to better performances for larger objects. For example, the model with  $T = 2$  and the model with  $T = 10000$  have similar AP results, but the former has better performances on  $\mathrm{AP}_S$  and  $\mathrm{AP}_M$ , while the latter works better on  $\mathrm{AP}_L$ , which also validates the role of positional priors in DETR.

Table 6: Comparison of models with different temperatures. All models are trained with the ResNet-50 backbone, batch size 64, no multiple pattern embeddings, and no modulated attentions. Default Settings are used for the rest of the parameters.  

<table><tr><td>Temperature</td><td>AP</td><td>AP50</td><td>AP75</td><td>APS</td><td>APM</td><td>APL</td></tr><tr><td>2</td><td>39.6</td><td>60.7</td><td>41.9</td><td>19.3</td><td>43.3</td><td>58.0</td></tr><tr><td>5</td><td>40.0</td><td>61.1</td><td>42.1</td><td>19.5</td><td>43.4</td><td>58.9</td></tr><tr><td>10</td><td>40.0</td><td>61.1</td><td>42.3</td><td>19.7</td><td>43.5</td><td>59.3</td></tr><tr><td>20</td><td>40.1</td><td>61.1</td><td>42.8</td><td>19.8</td><td>43.7</td><td>58.6</td></tr><tr><td>50</td><td>39.8</td><td>61.0</td><td>42.2</td><td>19.7</td><td>43.2</td><td>58.8</td></tr><tr><td>100</td><td>39.8</td><td>60.8</td><td>42.1</td><td>19.3</td><td>43.3</td><td>58.4</td></tr><tr><td>10000</td><td>39.5</td><td>60.7</td><td>41.7</td><td>18.9</td><td>42.6</td><td>58.9</td></tr></table>

# F RESULTS WITH LESS DECODER LAYERS

Table 7 shows the results of models with different decoder layers. All models are trained under our standard ResNet-50-DC setting except the number of decoder layers.  
Table 7: Comparison of models with different number of decoder layers. All models are trained under our standard ResNet-50-DC setting except the number of decoder layers.  

<table><tr><td>decoder layers</td><td>GFLOPs</td><td>Parmas</td><td>AP</td><td>\( AP_{50} \)</td><td>\( AP_{75} \)</td><td>\( AP_S \)</td><td>\( AP_M \)</td><td>\( AP_L \)</td></tr><tr><td>2</td><td>202</td><td>36M</td><td>40.2</td><td>59.0</td><td>42.9</td><td>22.2</td><td>43.5</td><td>55.4</td></tr><tr><td>3</td><td>206</td><td>38M</td><td>43.9</td><td>63.4</td><td>47.4</td><td>24.6</td><td>47.8</td><td>60.5</td></tr><tr><td>4</td><td>210</td><td>40M</td><td>44.9</td><td>64.5</td><td>48.2</td><td>25.9</td><td>48.5</td><td>61.0</td></tr><tr><td>5</td><td>213</td><td>42M</td><td>45.2</td><td>65.5</td><td>48.6</td><td>26.6</td><td>48.9</td><td>62.3</td></tr><tr><td>6</td><td>216</td><td>44M</td><td>45.7</td><td>66.2</td><td>49.0</td><td>26.1</td><td>49.4</td><td>63.1</td></tr></table>

# G FIXED  $x,y$  FOR BETTER PERFORMANCE

We provide in this section an interesting experiment. As we all know, all box coordinates  $x, y, h, w$  are learned from data. When we fix  $x, y$  of the anchor boxes with the random initialization, the model's performance increases consistently. The comparison of standard DAB-DETR and DAB-DETR with fixed  $x, y$  coordinates are shown in Table 8. Note that we only fix  $x, y$  at the first layer to prevent them from learning information from data. But  $x, y$  will be updated in other layers. We conjecture that the randomly initialized and fixed  $x, y$  coordinates can help to avoid overfitting, which may account for this phenomenon.

# H COMPARISON OF BOX UPDATE

To further demonstrate the effectiveness of our dynamic anchor box design, we plot the layer-by-layer update result of boxes of DAB-DETR and Conditional DETR in Fig. 11. All DETR-like models have a stacked layers structure. Hence the outputs of each layer can be viewed as a refining procedure. However, due to the high-dimensional queries that are shared across all layers, the update of queries between layers is not stable. As shaded in yellow in Fig. 11 (b), some boxes predicted in latter layers are worse than their previous layers.

# I ANALYSIS OF FAILURE CASES

Fig. 12 presents some samples where our model does not predict well. We find our model may have some troubles when facing dense objects, very small objects, or very large objects in an image. To

Table 8: Comparison of DAB-DETR and DAB-DETR with fixed anchor centers  $x, y$ . When fixing  $x, y$  of queries with random values, the performance of the models is improved consistently. The models with superscript * use 3 pattern embeddings as in Anchor DETR.  

<table><tr><td>Model</td><td>AP</td><td>\( AP_{50} \)</td><td>\( AP_{75} \)</td><td>\( AP_S \)</td><td>\( AP_M \)</td><td>\( AP_L \)</td></tr><tr><td>DAB-DETR-R50*</td><td>42.6</td><td>63.2</td><td>45.6</td><td>21.8</td><td>46.2</td><td>61.1</td></tr><tr><td>DAB-DETR-R50*-fixedx&amp;y</td><td>42.9(+0.3)</td><td>63.7</td><td>45.3</td><td>22.0</td><td>46.8</td><td>60.9</td></tr><tr><td>DAB-DETR-DC5-R50</td><td>44.5</td><td>65.1</td><td>47.7</td><td>25.3</td><td>48.2</td><td>62.3</td></tr><tr><td>DAB-DETR-DC5-R50-fixedx&amp;y</td><td>44.7(+0.2)</td><td>65.3</td><td>47.9</td><td>24.9</td><td>48.2</td><td>62.0</td></tr><tr><td>DAB-DETR-DC5-R50*</td><td>45.7</td><td>66.2</td><td>49.0</td><td>26.1</td><td>49.4</td><td>63.1</td></tr><tr><td>DAB-DETR-DC5-R50*-fixedx&amp;y</td><td>45.8(+0.1)</td><td>66.5</td><td>48.9</td><td>26.4</td><td>49.6</td><td>62.7</td></tr><tr><td>DAB-DETR-R101*</td><td>44.1</td><td>64.7</td><td>47.2</td><td>24.1</td><td>48.2</td><td>62.9</td></tr><tr><td>DAB-DETR-R101*-fixedx&amp;y</td><td>44.8(+0.7)</td><td>65.4</td><td>48.2</td><td>25.1</td><td>48.9</td><td>63.1</td></tr><tr><td>DAB-DETR-DC5-R101*</td><td>46.6</td><td>67.0</td><td>50.2</td><td>28.1</td><td>50.5</td><td>64.1</td></tr><tr><td>DAB-DETR-DC5-R101*-fixedx&amp;y</td><td>46.7(+0.1)</td><td>67.3</td><td>50.7</td><td>27.3</td><td>50.9</td><td>64.1</td></tr></table>

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/957505243b1d0b80ae83ffabfcacc19cf5d3e86dad40225bdd0926fe155d0f90.jpg)  
layer3

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/7a959dd65cd27d321b880550e8bae5da3a4d0c49f0f64a0d2ad5defcbd387842.jpg)  
layer4

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/893f302db7e71b379d8cfaeddbc89959ccfff8a611aae197a8b0950fd50904fc.jpg)  
layer3

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/9ae12522672cd1b1321c04aeca9753cb7fecebfaaef968b80efc6abaccf0454d.jpg)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/dc0d1c52a7805b3049cafd7da9f62c27962842747de4a1bbe510a9300c3cc0bf.jpg)  
layer2

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/7e70110806f1716b412a741610e1905f126832e49910f14161f08ba63cb8dc26.jpg)  
layer3

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/4b21879c4b906de1e048a34128a002838a27be6ef7218abfbd9f13b35b4623ef.jpg)  
layer2

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/0305a869dbdeb29eaf279c7c55afd9d509d9d5f9968cb8f875b0ad6fac9965e5.jpg)  
layer4  
layer3

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/58db60684dd735e92a70891b3bcf7c6d53f72a452a21b18beaca256213534d91.jpg)  
layer4  
a) DAB-DETR  
Figure 11: We compare the layer-by-layer update of boxes of DAB-DETR (a) and Conditional DETR (b). The green boxes are ground truth annotations while red boxes are model predictions. The boxes of Conditional DETR have larger variances and we mark some boundaries of boxes with a large change in yellow.

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/b940aa1f88951c53aa751fa9688c32fccd9215abfd039415c1bf27dc79beffb9.jpg)  
layer5

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/aa47cb62c20c05e87cdf65f936a5ff4faf8b6a8d41fc02538d4fff586e413f9f.jpg)  
layer4  
b) Conditional DETR

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/f3937f11110d4ced196c390e4f30e210c179bab65d1a421e24321669bc4e7e0b.jpg)  
layer5

improve the performance of our model, we will introduce a multi-scale technique into our model to improve the detection performance on small and large objects.

# J COMPARISON OF RUNTIME

We compare the runtime of DETR, Conditional DETR, and our proposed DAB-DETR in Table 9. Their runtime speeds are reported on a single Nvidia A100 GPU. Our DAB-DETR has a similar inference speed but better performance compared with Conditional DETR, which is our direct competitor.

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/92297e17c1cef5e4c4ab3220f667b97d814986ee07d5556ad7b987320f81d3fd.jpg)  
(a)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/8f250234f0ef89a139d2534ecc0119bd56eae62717c272cfc3caf7aae0d7dff3.jpg)  
(b)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/0c8a9e551a1eb1eb06786f055ba481e49d7556fe01640a7d4685b0dedd1213b6.jpg)  
(c)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/d69bc97f1709a68033be360329007b1d680a0f07ee3345070f5d87168e90c28b.jpg)  
(d)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/83a92dc15b8baf51c7e8d0b9e0eec30af85d9320552943a0096f2739d11dbdbc.jpg)  
(e)

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/986485a82a231d19fbeb3df449272f8c34552672e645105fa3f7ccda743e7990.jpg)  
Figure 12: We visualize some images where our model does not predict well, including dense objects (a,b,c), very small objects (d), and very large objects (e,f). The green boxes are ground truth annotations while red boxes are predictions of models.  
(f)

Table 9: Comparison of the runtime of DETR, Conditional DETR, and our proposed DAB-DETR. All speeds are reported on a single Nvidia A100 GPU.  

<table><tr><td>Model</td><td>time(s/img)</td><td>epochs</td><td>AP</td><td>\( AP_{50} \)</td><td>\( AP_{75} \)</td><td>\( AP_S \)</td><td>\( AP_M \)</td><td>\( AP_L \)</td><td>Parmas</td></tr><tr><td>DETR-R50</td><td>0.048</td><td>500</td><td>42.0</td><td>62.4</td><td>44.2</td><td>20.5</td><td>45.8</td><td>61.1</td><td>41M</td></tr><tr><td>Conditional DETR-R50</td><td>0.057</td><td>50</td><td>40.9</td><td>61.8</td><td>43.3</td><td>20.8</td><td>44.6</td><td>59.2</td><td>44M</td></tr><tr><td>DAB-DETR-R50</td><td>0.059</td><td>50</td><td>42.2</td><td>63.1</td><td>44.7</td><td>21.5</td><td>45.7</td><td>60.3</td><td>44M</td></tr><tr><td>DETR-R101</td><td>0.074</td><td>500</td><td>43.5</td><td>63.8</td><td>46.4</td><td>21.9</td><td>48.0</td><td>61.8</td><td>60M</td></tr><tr><td>Conditional DETR-R101</td><td>0.082</td><td>50</td><td>42.8</td><td>63.7</td><td>46.0</td><td>21.7</td><td>46.6</td><td>60.9</td><td>63M</td></tr><tr><td>DAB-DETR-R101</td><td>0.085</td><td>50</td><td>43.5</td><td>63.9</td><td>46.6</td><td>23.6</td><td>47.3</td><td>61.5</td><td>63M</td></tr></table>

# K COMPARISON OF MODEL CONVERGENCE

We present convergence curves of DETR, Conditional DETR, and out DAB-DETR in Fig. 13. All models are trained under standard R50(DC5) setting. The results demonstrate the effectiveness of our model. Our DAB-DETR is trained with our fix  $x \& y$  variants. See Appendix G for more details about the fix  $x \& y$  results. Both the Conditional DETR and our DAB-DETR use 300 queries, while DETR leverages 100 queries.

Our DAB-DETR converges faster than Conditional DETR, especially on the early epochs, as shown in Fig. 13.

![](https://cdn-mineru.openxlab.org.cn/result/2025-10-30/188481c5-b3af-48b0-8df9-0442c08ce38f/737bacd101b23d10d853b3db884723fc03aa858b33045587ed0bb0639b7e1957.jpg)  
Figure 13: Convergence curves of DETR, Conditional DETR, and our DAB-DETR. All models are trained under the R50(DC5) setting.