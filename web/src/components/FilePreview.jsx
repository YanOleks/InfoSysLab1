import React, { useState, useEffect } from 'react';
import { Modal, Spin, message } from 'antd';
import api from '../api';

export default function FilePreview({ file, onClose }) {
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let objectUrl = null;
    const fetchPreview = async () => {
      try {
        if (file.extension === '.py') {
          const res = await api.get(`/files/${file.id}/preview`);
          setContent(res.data.content);
        } else if (file.extension === '.jpg') {
          const res = await api.get(`/files/${file.id}/preview`, { responseType: 'blob' });
          objectUrl = URL.createObjectURL(res.data);
          setContent(objectUrl);
        }
      } catch (err) {
        message.error('Failed to load preview');
        onClose();
      }
      setLoading(false);
    };
    fetchPreview();
    
    return () => {
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [file, onClose]);

  return (
    <Modal
      title={file.filename}
      open={!!file}
      onCancel={onClose}
      footer={null}
      width={800}
    >
      {loading ? (
        <div style={{ textAlign: 'center', padding: '20px' }}><Spin /></div>
      ) : (
        file.extension === '.py' ? (
          <pre style={{ background: '#f5f5f5', padding: '16px', overflowX: 'auto', borderRadius: '4px' }}>
            <code>{content}</code>
          </pre>
        ) : file.extension === '.jpg' ? (
          <div style={{ textAlign: 'center' }}>
            <img 
              src={content} 
              alt={file.filename} 
              style={{ maxWidth: '100%', maxHeight: '70vh', objectFit: 'contain' }} 
            />
          </div>
        ) : (
          <p>Preview is not available for this file type</p>
        )
      )}
    </Modal>
  );
}
