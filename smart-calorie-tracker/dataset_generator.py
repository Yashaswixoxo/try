
# import os
# import shutil
# import urllib.request
# from PIL import Image
# import numpy as np

# DATASET_DIR = 'food_dataset'
# FOOD_CATEGORIES = [
#     'apple', 'banana', 'pizza', 'burger', 'rice', 'chicken', 
#     'salad', 'pasta', 'bread', 'egg', 'fish', 'steak',
#     'sandwich', 'soup', 'cake', 'cookie', 'donut', 'fries',
#     'hotdog', 'ice_cream', 'orange', 'strawberry', 'watermelon',
#     'broccoli', 'carrot', 'tomato', 'potato', 'cheese'
# ]

# def create_dataset_structure():
#     """Create directory structure for the dataset"""
#     os.makedirs(DATASET_DIR, exist_ok=True)
    
#     for category in FOOD_CATEGORIES:
#         category_dir = os.path.join(DATASET_DIR, category)
#         os.makedirs(category_dir, exist_ok=True)
#         print(f"Created directory: {category_dir}")
    
#     print(f"\nDataset structure created at: {DATASET_DIR}")
#     print(f"Total categories: {len(FOOD_CATEGORIES)}")

# def download_food101_dataset():
#     """
#     Instructions to download Food-101 dataset
#     Food-101 is a popular dataset with 101 food categories and 101,000 images
#     """
#     print("""
#     To use the Food-101 dataset:
    
#     1. Download from: https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/
#     2. Extract the archive
#     3. Run organize_food101_data() to organize it for training
    
#     Alternative: Use Kaggle's Food-101 dataset
#     1. Install kaggle: pip install kaggle
#     2. Download: kaggle datasets download -d dansbecker/food-101
#     3. Extract and organize
#     """)

# def organize_food101_data(food101_dir, output_dir=DATASET_DIR):
#     """
#     Organize Food-101 dataset into our structure
#     Only keeps the categories we need
#     """
#     images_dir = os.path.join(food101_dir, 'images')
    
#     for category in FOOD_CATEGORIES:
#         src_dir = os.path.join(images_dir, category)
#         dst_dir = os.path.join(output_dir, category)
        
#         if os.path.exists(src_dir):
#             os.makedirs(dst_dir, exist_ok=True)
            
#             images = os.listdir(src_dir)
#             for img in images[:1000]:  # Limit to 1000 images per category
#                 src_path = os.path.join(src_dir, img)
#                 dst_path = os.path.join(dst_dir, img)
#                 shutil.copy2(src_path, dst_path)
            
#             print(f"Copied {len(os.listdir(dst_dir))} images for {category}")
#         else:
#             print(f"Warning: {category} not found in Food-101 dataset")

# def validate_dataset(dataset_dir=DATASET_DIR):
#     """Validate and report dataset statistics"""
#     print("\n=== Dataset Validation ===\n")
    
#     total_images = 0
#     category_counts = {}
    
#     for category in os.listdir(dataset_dir):
#         category_path = os.path.join(dataset_dir, category)
#         if os.path.isdir(category_path):
#             count = len([f for f in os.listdir(category_path) 
#                         if f.endswith(('.jpg', '.jpeg', '.png'))])
#             category_counts[category] = count
#             total_images += count
    
#     print(f"Total categories: {len(category_counts)}")
#     print(f"Total images: {total_images}")
#     print(f"\nImages per category:")
#     for category, count in sorted(category_counts.items()):
#         print(f"  {category}: {count}")
    
#     # Check for imbalanced dataset
#     if category_counts:
#         avg_count = total_images / len(category_counts)
#         print(f"\nAverage images per category: {avg_count:.0f}")
        
#         min_cat = min(category_counts, key=category_counts.get)
#         max_cat = max(category_counts, key=category_counts.get)
#         print(f"Min: {min_cat} ({category_counts[min_cat]})")
#         print(f"Max: {max_cat} ({category_counts[max_cat]})")

# def augment_dataset(category_dir, target_count=1000):
#     """
#     Augment images in a category to reach target count
#     Uses random transformations
#     """
#     from PIL import ImageEnhance, ImageOps
    
#     images = [f for f in os.listdir(category_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
#     current_count = len(images)
    
#     if current_count >= target_count:
#         return
    
#     needed = target_count - current_count
#     print(f"Augmenting {os.path.basename(category_dir)}: adding {needed} images")
    
#     transformations = [
#         lambda img: img.transpose(Image.FLIP_LEFT_RIGHT),
#         lambda img: img.rotate(15),
#         lambda img: img.rotate(-15),
#         lambda img: ImageEnhance.Brightness(img).enhance(1.2),
#         lambda img: ImageEnhance.Brightness(img).enhance(0.8),
#         lambda img: ImageEnhance.Contrast(img).enhance(1.2),
#         lambda img: ImageEnhance.Contrast(img).enhance(0.8),
#     ]
    
#     for i in range(needed):
#         # Pick a random original image
#         src_img_name = np.random.choice(images)
#         src_path = os.path.join(category_dir, src_img_name)
        
#         try:
#             img = Image.open(src_path)
            
#             # Apply random transformation
#             transform = np.random.choice(transformations)
#             augmented_img = transform(img)
            
#             # Save with new name
#             new_name = f"aug_{i}_{src_img_name}"
#             new_path = os.path.join(category_dir, new_name)
#             augmented_img.save(new_path)
            
#         except Exception as e:
#             print(f"Error augmenting {src_img_name}: {e}")

# def split_dataset(dataset_dir=DATASET_DIR, train_ratio=0.8):
#     """Split dataset into train and validation sets"""
#     train_dir = os.path.join(dataset_dir, 'train')
#     val_dir = os.path.join(dataset_dir, 'validation')
    
#     os.makedirs(train_dir, exist_ok=True)
#     os.makedirs(val_dir, exist_ok=True)
    
#     for category in os.listdir(dataset_dir):
#         category_path = os.path.join(dataset_dir, category)
        
#         if not os.path.isdir(category_path) or category in ['train', 'validation']:
#             continue
        
#         images = [f for f in os.listdir(category_path) 
#                  if f.endswith(('.jpg', '.jpeg', '.png'))]
        
#         np.random.shuffle(images)
#         split_idx = int(len(images) * train_ratio)
        
#         train_images = images[:split_idx]
#         val_images = images[split_idx:]
        
#         # Create category dirs
#         train_cat_dir = os.path.join(train_dir, category)
#         val_cat_dir = os.path.join(val_dir, category)
#         os.makedirs(train_cat_dir, exist_ok=True)
#         os.makedirs(val_cat_dir, exist_ok=True)
        
#         # Copy files
#         for img in train_images:
#             src = os.path.join(category_path, img)
#             dst = os.path.join(train_cat_dir, img)
#             shutil.copy2(src, dst)
        
#         for img in val_images:
#             src = os.path.join(category_path, img)
#             dst = os.path.join(val_cat_dir, img)
#             shutil.copy2(src, dst)
        
#         print(f"{category}: {len(train_images)} train, {len(val_images)} validation")

# if __name__ == '__main__':
#     print("=== Food Dataset Generator ===\n")
#     print("1. Create dataset structure")
#     print("2. Download/organize Food-101")
#     print("3. Validate dataset")
#     print("4. Augment dataset")
#     print("5. Split into train/validation")
    
#     # Create structure
#     create_dataset_structure()
    
#     # Instructions
#     print("\n" + "="*50)
#     print("Next steps:")
#     print("1. Manually add food images to each category folder")
#     print("2. Or download Food-101 dataset and organize it")
#     print("3. Run validate_dataset() to check")
#     print("4. Run augment_dataset() if needed")
#     print("5. Run split_dataset() before training")