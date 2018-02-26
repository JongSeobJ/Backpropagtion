import numpy as np
class activation:
        def forward(self,x,method='sigmoid'):
            x = np.array(x)
            if method.lower() == 'sigmoid':
                return 1/(1+np.exp(-x))
            if method.lower() == 'relu':
                x[x<0] = 0 
                return x

        def backward(self,x,method='sigmoid'):
            x = np.array(x)
            if method.lower() == 'sigmoid':
                return x*(1-x)
            if method.lower() == 'relu':
                x[x<0] = 0 
                x[x>0] = 1
                return x
##
class layers:
    def weight(self,shape=[None,None]):
        return np.random.normal(size = shape) / np.sqrt(shape[0]/2)

    def layer(self,X,W,b,active='sigmoid'):
        if type(X) is dict:
            X_t = X['out']
            #out = activation().forward(X_t.dot(W)+b,active)
            out = activation().forward(X_t.dot(W),active)
            out_back = activation().backward(out,active)
            return dict(out=out, out_back=out_back, weight=W, bias=b, active=active, net= X_t)
        else:
            X_t = np.array(X)
            #out = np.array(X_t).dot(W)+b
            out = np.array(X_t).dot(W)
            out = activation().forward(out,active)
            out_back = activation().backward(out,active)
            return dict(out=out, out_back=out_back, weight=W, bias=b, active=active, net= X_t)
    def train_data(self,shape=[None,None]):
        return np.zeros(shape[1])

##
class optimizer:
    def loss(self,real,predict,loss_type='mse'):
        #y[iteration],out[len(out)-1],
        if loss_type.lower() == 'mse':
            return np.array(predict) - np.array(real)
        if loss_type.lower() == 'cross_entropy':
            return np.array(real) * np.array(predict)
        
    def accuracy(self,pred,real):
        count = 0 
        pred = np.argmax(pred,axis=1)
        real = np.where(real==1)[1]
        for i in range(len(pred)):
            if pred[i]==real[i]:
                count += 1
        return count/len(pred)

    def SGD(self,x,y,layer,loss_type,lr=0.01,epoch=10):
        def layer_cal(train_data,weight,bias):
            layer[0] = layers().layer(train_data,weight[0],bias[0])
            for la in range(1,len(weight)):
                layer[la] = layers().layer(layer[la-1]['out'],weight[la],bias[la])
            return layer
        
        def dictionary(layer):
            out = dict();out_back = dict();weight = dict();bias = dict();active = dict();net = dict()
            for i in range(len(layer)):
                out[i]    = layer[i]['out']
                out_back[i] = layer[i]['out_back']
                weight[i] = layer[i]['weight']
                bias[i]   = np.array(layer[i]['bias'])
                active[i] = layer[i]['active']
                net[i]    = np.array(layer[i]['net'])
            return out,out_back,weight,bias,active,net
        
        def out_net_cal(out,out_back):
            out_net = dict()
            for i in reversed(range(len(out))):
                out_net_temp = np.eye(out[i].shape[0])
                np.fill_diagonal(out_net_temp,out_back[i])
                out_net[i] = out_net_temp
            return out_net
        
        def training(loss_val,out_net,out_back,weight,bias):
            w_update = dict(); b_update=dict()
            for idx in reversed(range(len(weight))):
                update = np.array(loss_val)
                for i in reversed(range(idx,len(weight))):
                    if i == idx:
                        b_upd = (update.dot(out_net[i]))
                        update = update.dot(out_net[i])
                        update = net[i].reshape(net[i].shape[0],1).dot(update.reshape(1,update.shape[0]))
                    else:
                        update = (update.dot(out_net[i])).dot(weight[i].T)
                w_update[idx] = update
                b_update[idx] = b_upd
            return w_update, b_update
        
        ## 전체 data set 
        out,out_back,weight,bias,active,net = dictionary(layer)
        for ep in range(epoch):
            for iteration in range(len(x)):
                layer = layer_cal(x[iteration],weight,bias)
                #print(layer)
                out,out_back,_,_,active,net = dictionary(layer)
                out_net = out_net_cal(out,out_back)
                loss_val = self.loss(y[iteration],out[len(out)-1],loss_type)
                #print(loss_val,out[len(out)-1])
                w_update, b_update = training(loss_val,out_net,out_back,weight,bias)
                #print(w_update,b_update)
                ## update
                for i in range(len(weight)):
                    weight[i] = weight[i] - lr*w_update[i]
                    bias[i] = bias[i] - lr*b_update[i]
                ## feed_again
            if ep % 10 == 0:
                #temp = activation().forward(np.array(x).dot(weight[0])+bias[0],active[0])
                temp = activation().forward(np.array(x).dot(weight[0]),active[0])
                for i in range(1,len(weight)):
                    #temp =  activation().forward(temp.dot(weight[i])+bias[i],active[i])
                    temp =  activation().forward(temp.dot(weight[i]),active[i])
                print(self.accuracy(temp,y))
                
        return dict(weight=weight,bias=bias)