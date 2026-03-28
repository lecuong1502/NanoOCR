import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";

const ACCEPTED = {
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/tiff': ['.tif', '.tiff'],
    'image/webp': ['.webp'],
    'application/pdf': ['.pdf'],
};

interface Props {
    onFileSelect: (file: File) => void
    isLoading: boolean
};

export default function FileUploader({ onFileSelect, isLoading }: Props) {
    const [preview, setPreview] = useState<string | null>(null);
    const [fileName, setFileName] = useState<string | null>(null);

    const onDrop = useCallback((accepted: File[]) => {
        const file = accepted[0]
        if (!file) return
        setFileName(file.name)
        if (file.type.startsWith('image/')) {
            setPreview(URL.createObjectURL(file))
        } else {
            setPreview(null)
        }
        onFileSelect(file)
    }, [onFileSelect]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: ACCEPTED,
        maxFiles: 1,
        disabled: isLoading,
    });

    return (
        <div className="flex flex-col gap-4">
            <div
                {...getRootProps()}
                className={[
                'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors',
                isDragActive ? 'border-sky-500 bg-sky-50' : 'border-gray-300 hover:border-sky-400 hover:bg-gray-50',
                isLoading ? 'opacity-50 cursor-not-allowed' : '',
                ].join(' ')}
            >
                <input {...getInputProps()}></input>
                <div className="flex flex-col items-center gap-3">
                    {isDragActive ? (
                        <p className="text-sky-600 font-medium">Drop the file here</p>
                    ) : (
                        <>
                            <p className="text-gray-600 font-medium">Drag and drop or click to browse</p>
                            <p className="text-xs text-gray-400">JPG · PNG · TIFF · WebP · PDF</p>
                        </>
                    )}
                </div>
            </div>
            {preview && (
                <div className="rounded-lg overflow-hidden border border-gray-200">
                    <img src={preview} alt="Preview" className="w-full object-contain max-h-64" />
                </div>
            )}
            {fileName && !preview && (
                <div className="flex items-center gap-2 p-3 bg-gray-100 rounded-lg text-sm text-gray-700">
                    <span className="truncate">{fileName}</span>
                </div>
            )}
        </div>
    );
};