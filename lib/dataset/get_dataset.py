import torchvision.transforms as transforms
from dataset.cocodataset import CoCoDataset
from utils.cutout import SLCutoutPIL
from randaugment import RandAugment
import os.path as osp
import os
from dataset.odir_dataset import OdirDataset

def get_datasets(args):
    if args.orid_norm:
        normalize = transforms.Normalize(mean=[0, 0, 0],
                                         std=[1, 1, 1])
        # print("mean=[0, 0, 0], std=[1, 1, 1]")
    else:
        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
        # print("mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]")

    train_data_transform_list = [transforms.Resize((args.img_size, args.img_size)),
                                            RandAugment(),
                                               transforms.ToTensor(),
                                               normalize]
    try:
        # for q2l_infer scripts
        if args.cutout:
            print("Using Cutout!!!")
            train_data_transform_list.insert(1, SLCutoutPIL(n_holes=args.n_holes, length=args.length))
    except Exception as e:
        Warning(e)
    train_data_transform = transforms.Compose(train_data_transform_list)

    test_data_transform = transforms.Compose([
                                            transforms.Resize((args.img_size, args.img_size)),
                                            transforms.ToTensor(),
                                            normalize])
    

    if args.dataname == 'coco' or args.dataname == 'coco14':
        # ! config your data path here.
        dataset_dir = args.dataset_dir
        train_dataset = CoCoDataset(
            image_dir=osp.join(dataset_dir, 'train2014'),
            anno_path=osp.join(dataset_dir, 'annotations/instances_train2014.json'),
            input_transform=train_data_transform,
            labels_path='data/coco/train_label_vectors_coco14.npy',
        )
        val_dataset = CoCoDataset(
            image_dir=osp.join(dataset_dir, 'val2014'),
            anno_path=osp.join(dataset_dir, 'annotations/instances_val2014.json'),
            input_transform=test_data_transform,
            labels_path='data/coco/val_label_vectors_coco14.npy',
        )  

    elif args.dataname == 'odir':
        odir_root = '/kaggle/working'
        scale_size = 640

        normTransform = transforms.Normalize(mean=[0.5], std=[0.5])

        trainTransform = transforms.Compose([transforms.Resize((scale_size, scale_size)),
                                        transforms.RandomHorizontalFlip(),
                                        normTransform
        ])

        testTransform = transforms.Compose([transforms.Resize((scale_size, scale_size)),
                                            normTransform
        ])

        train_dataset = OdirDataset(
            split='train',
            data_file=os.path.join(odir_root, 'odir.npz'),
            transform=trainTransform,
            )
        val_dataset = OdirDataset(
            split='val',
            data_file=os.path.join(odir_root, 'odir.npz'),
            transform=testTransform,
            )
        test_dataset = OdirDataset(
            split='test',
            data_file=os.path.join(odir_root, 'odir.npz'),
            transform=testTransform,
            )  

    else:
        raise NotImplementedError("Unknown dataname %s" % args.dataname)

    print("len(train_dataset):", len(train_dataset)) 
    print("len(val_dataset):", len(val_dataset))

    return train_dataset, val_dataset
