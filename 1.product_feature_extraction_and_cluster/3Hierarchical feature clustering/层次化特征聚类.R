X = read.table('G:/论文实验——隐含情感分析/1特征提取/3层次化特征构建/PMImat.txt',,header=TRUE,sep=",")
rownames(X) = colnames(X)
Y <- as.dist(X);Y
hc1 <- hclust(Y,"average")
#cbind(hc1$merge,hc1$height)
plot(hc1,hang = -1,cex=.8)