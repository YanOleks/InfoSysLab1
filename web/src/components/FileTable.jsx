import React, { useState } from 'react';
import { Table, Button, Popconfirm, message, Radio, Checkbox, Dropdown, Space } from 'antd';
import { DownOutlined } from '@ant-design/icons';
import api from '../api';
import FilePreview from './FilePreview';

export default function FileTable({ files, loading, onRefresh, filterExt, setFilterExt }) {
  const [previewFile, setPreviewFile] = useState(null);
  
  const defaultColumns = ['extension', 'created_at', 'updated_at', 'uploaded_by', 'modified_by'];
  const [visibleColumns, setVisibleColumns] = useState(defaultColumns);

  const downloadFile = async (id, filename) => {
    try {
      const res = await api.get(`/files/${id}/download`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (err) {
      message.error('Download failed');
    }
  };

  const deleteFile = async (id) => {
    try {
      await api.delete(`/files/${id}`);
      message.success('File deleted');
      onRefresh();
    } catch (err) {
      message.error('Delete failed');
    }
  };

  const allColumns = [
    { title: 'Назва', dataIndex: 'filename', key: 'filename', fixed: true },
    { 
      title: 'Тип', 
      dataIndex: 'extension', 
      key: 'extension',
      sorter: (a, b) => a.extension.localeCompare(b.extension) 
    },
    { title: 'Дата створення', dataIndex: 'created_at', key: 'created_at' },
    { title: 'Дата зміни', dataIndex: 'updated_at', key: 'updated_at' },
    { title: 'Завантажив', dataIndex: 'uploaded_by_username', key: 'uploaded_by' },
    { title: 'Останній редактор', dataIndex: 'last_modified_by_username', key: 'modified_by' },
    { 
      title: 'Дії', 
      key: 'actions', 
      render: (_, record) => (
        <div onClick={e => e.stopPropagation()}>
          <Space>
            <Button onClick={() => downloadFile(record.id, record.filename)}>Download</Button>
            <Popconfirm title="Видалити?" onConfirm={() => deleteFile(record.id)}>
              <Button danger>Delete</Button>
            </Popconfirm>
          </Space>
        </div>
      )
    }
  ];

  const filteredColumns = allColumns.filter(col => 
    col.key === 'filename' || col.key === 'actions' || visibleColumns.includes(col.key)
  );

  const columnMenu = (
    <div style={{ background: '#fff', padding: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.15)', borderRadius: 4 }}>
      <Checkbox.Group 
        options={[
          { label: 'Тип', value: 'extension' },
          { label: 'Дата створення', value: 'created_at' },
          { label: 'Дата зміни', value: 'updated_at' },
          { label: 'Завантажив', value: 'uploaded_by' },
          { label: 'Останній редактор', value: 'modified_by' }
        ]}
        value={visibleColumns}
        onChange={setVisibleColumns}
        style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}
      />
    </div>
  );

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Radio.Group 
          value={filterExt || 'all'} 
          onChange={e => setFilterExt(e.target.value === 'all' ? null : e.target.value)}
        >
          <Radio.Button value="all">Всі файли</Radio.Button>
          <Radio.Button value="js_png">Тільки .js та .png</Radio.Button>
        </Radio.Group>
        
        <Dropdown dropdownRender={() => columnMenu} trigger={['click']}>
          <Button>
            Стовпці <DownOutlined />
          </Button>
        </Dropdown>
      </div>

      <Table 
        rowKey="id"
        dataSource={files} 
        columns={filteredColumns} 
        loading={loading}
        onRow={(record) => ({ 
          onClick: () => {
            const ext = record.extension.toLowerCase();
            if (ext === '.py' || ext === '.jpg') {
              setPreviewFile(record);
            } else {
              message.info("Preview is not available for this file type");
            }
          },
          style: { cursor: 'pointer' }
        })}
      />

      {previewFile && (
        <FilePreview 
          file={previewFile} 
          onClose={() => setPreviewFile(null)} 
        />
      )}
    </div>
  );
}
