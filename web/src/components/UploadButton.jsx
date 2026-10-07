import React from 'react';
import { Upload, message } from 'antd';

const { Dragger } = Upload;

export default function UploadButton({ onUploadComplete }) {
  const props = {
    name: 'file',
    multiple: false,
    showUploadList: false,
    action: 'http://localhost:8000/files/upload',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    onChange(info) {
      const { status } = info.file;
      if (status === 'done') {
        message.success(`${info.file.name} uploaded successfully.`);
        onUploadComplete();
      } else if (status === 'error') {
        message.error(`${info.file.name} upload failed.`);
      }
    },
  };

  return (
    <Dragger {...props} style={{ padding: '20px', background: '#fafafa' }}>
      <p style={{ fontSize: '24px', color: '#1890ff', margin: 0 }}>📁</p>
      <p className="ant-upload-text">Click or drag file to this area to upload</p>
    </Dragger>
  );
}
