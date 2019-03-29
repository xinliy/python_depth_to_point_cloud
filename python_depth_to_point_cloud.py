from PIL import Image
import pandas as pd
import numpy as np
import os
from open3d import read_point_cloud,draw_geometries


class point_cloud_generator():

    def __init__(self, rgb_file, depth_file, pc_file, focal_length, scalingfactor):
        self.rgb_file = rgb_file
        self.depth_file = depth_file
        self.pc_file = pc_file
        self.focal_length = focal_length
        self.scalingfactor = scalingfactor
        self.rgb = Image.open(rgb_file)
        self.depth = Image.open(depth_file).convert('I')
        # print(self.depth.size)
        self.width = self.rgb.size[0]
        self.height = self.rgb.size[1]

    def calculate(self):
        depth = np.asarray(self.depth).T
        # print(depth)
        # depth=np.swapaxes(depth,0,1)
        # print(depth.shape)
        self.Z = depth / self.scalingfactor
        X = np.zeros((self.width, self.height))
        Y = np.zeros((self.width, self.height))
        for i in range(self.width):
            X[i, :] = np.full(X.shape[1], i)

        self.X = ((X - self.width / 2) * self.Z) / self.focal_length
        for i in range(self.height):
            Y[:, i] = np.full(Y.shape[0], i)
        self.Y = ((Y - self.height / 2) * self.Z) / self.focal_length
        df = pd.DataFrame(columns=['x', 'y', 'z', 'r', 'g', 'b'])
        df.x = self.X.T.reshape(-1)
        df.y = self.Y.T.reshape(-1)
        df.z = self.Z.T.reshape(-1)
        img = np.array(self.rgb)
        df.r = img[:, :, 0:1].reshape(-1)
        df.g = img[:, :, 1:2].reshape(-1)
        df.b = img[:, :, 2:3].reshape(-1)
        df[['r', 'g', 'b']] = df[['r', 'g', 'b']].astype('uint8')

        self.df = df

    def write_ply(self):
        float_formatter = lambda x: "%.4f" % x
        points = []
        for index, row in self.df.iterrows():
            i=row.values

            points.append("{} {} {} {} {} {} 0\n".format
                      (float_formatter(i[0]), float_formatter(i[1]), float_formatter(i[2]),
                       int(i[3]), int(i[4]), int(i[5])))
    # point.append(a[col].tolist())
        file = open(self.pc_file, "w")
        file.write('''ply
        format ascii 1.0
        element vertex %d
        property float x
        property float y
        property float z
        property uchar red
        property uchar green
        property uchar blue
        property uchar alpha
        end_header
        %s
        ''' % (len(points), "".join(points)))
        file.close()


    def show_point_cloud(self):
        pcd=read_point_cloud(self.pc_file)
        draw_geometries([pcd])

a = point_cloud_generator('p1.png', 'd1.png', 'pc.ply',
                          focal_length=50, scalingfactor=1000)
a.calculate()
a.write_ply()
a.show_point_cloud()
