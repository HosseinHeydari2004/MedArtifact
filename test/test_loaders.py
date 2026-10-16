import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from medartifact.io import IOPipeline

io = IOPipeline()

<<<<<<< HEAD
# volume = image.data
#
# fig, axes = plt.subplots(1, 3, figsize=(15, 5))
#
# mid_x = volume.shape[0] // 2
# mid_y = volume.shape[1] // 2
# mid_z = volume.shape[2] // 2
#
# axes[0].imshow(volume[mid_x, :, :], cmap="gray")
# axes[0].set_title("Sagittal")
#
# axes[1].imshow(volume[:, mid_y, :], cmap="gray")
# axes[1].set_title("Coronal")
#
# axes[2].imshow(volume[:, :, mid_z], cmap="gray")
# axes[2].set_title("Axial")
#
# for ax in axes:
#     ax.axis("off")
#
# plt.show()

# plt.imshow(image.data, cmap="gray")
# plt.axis("off")
# plt.show()
# print(image.metadata.__sizeof__())

# loader = PipelineLoader(
#     path=r"C:\Users\hosse\Downloads\walnut_masked.nii"
# )
# image = loader.load()
#
# writer = NIfTIWriter()
#
# output_path = writer.write(
#     image=image,
#     output_path="example/corrected.nii.gz"
# )
# print(output_path)
#
# loader.path = "example/corrected.nii.gz"
#
# result = loader.load()
# print(loader.path)
# print(result.data.shape)
# print(result.data.dtype)
# print(result.affine)
=======
images, loaded_report = io.load(
    input_path=r"D:\AI Source\Projects\list_of_projects\cancer_pictures\brisc2025\classification_task"
)
print(loaded_report.summary())
>>>>>>> fe8bc5110aa11def094b7a469b33587c769c1d2d
