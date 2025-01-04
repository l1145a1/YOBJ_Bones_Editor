import struct
import sys
import os

bones=[]
bones_offset=[]
bones_name=[]
bones_parrent=[]
read_bones_offset= 0
bones_count = 0

def bones_list(f):
    global bones_count, read_bones_offset
    f.seek(28)
    bones_count=struct.unpack('<i', f.read(4))[0]
    print(f"bones count: {bones_count}")
    f.seek(40)
    read_bones_offset=struct.unpack('<i', f.read(4))[0]
    print(f"bones offset: {read_bones_offset+8}")
    f.seek(read_bones_offset+8)
    for i in range(bones_count):
        offset=f.tell()
        bones_offset.append(offset)
        pointer = f.read(16).decode('ascii')
        bones_name.append(pointer)
        f.read(32)
        pointer = struct.unpack('<i', f.read(4))[0]
        bones_parrent.append(pointer)
        f.seek(-52, 1)
        pointer = f.read(80)
        bones.append(pointer)
        pass
    for i in range(bones_count):
        name = bones_name[i]
        offset = bones_offset[i]
        parrent = bones_parrent[i]
        parrent_name = "none"
        if parrent != -1:
            parrent_name = bones_name[parrent]
            pass
        print(f"Index {i}, Name {name}, Offset {offset}, Parrent {parrent} ({parrent_name})")
        pass

def rename_bones(f, index):
    f.seek(bones_offset[index])
    print(f"Old Name: {bones_name[index]}")
    newname=input("New Name (max.16): ")[:16]
    bones_name[index]=newname
    newname=newname.encode('ascii')
    newname=newname.ljust(16, b'\x00')
    f.write(newname)
    f.seek(bones_offset[index])
    offset=f.tell()
    newname=f.read(16).decode('ascii')
    print(f"Write at Offset {offset}, Value {bones_name[index]}")
    pass

def change_parrent(f, index):
    global bones_count
    f.seek(bones_offset[index]+48)
    offset=f.tell()
    print(f"Name: {bones_name[index]}")
    parrent = bones_parrent[index]
    parrent_name = "none"
    if parrent != -1:
        parrent_name = bones_name[parrent]
        pass
    print(f"Old Parrent: {parrent} ({parrent_name})")
    newparrent=int(input("New Parrent: "))
    f.write(struct.pack('<i',newparrent))
    print(f"Write at Offset {offset}, Value {newparrent}")
    pass

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} infile")
        return 1

    try:
        yobj_file = open(sys.argv[1], "r+b")
    except IOError:
        print(f"Cannot open {sys.argv[1]}")
        return 1
    bones_list(yobj_file)
    print("Daftar Menu:")
    print("1. Rename Bones")
    print("2. Parrent Index Changer")
    menu=int(input("Pilih: "))
    index=int(input("Index : "))
    if menu==1:
        rename_bones(yobj_file,index)
        pass
    elif menu==2:
        change_parrent(yobj_file, index)
        pass
    yobj_file.close()

    return 0

if __name__ == "__main__":
    main()
