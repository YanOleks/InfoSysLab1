import React, { useState, useEffect } from 'react';
import { Layout, Button, Typography, Space } from 'antd';
import FileTable from '../components/FileTable';
import UploadButton from '../components/UploadButton';
import api from '../api';

const { Header, Content } = Layout;
const { Title } = Typography;

export default function DashboardPage({ onLogout }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterExt, setFilterExt] = useState(null);

  const loadFiles = async () => {
    setLoading(true);
    try {
      const params = filterExt ? { filter_ext: filterExt } : {};
      const res = await api.get('/files', { params });
      setFiles(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, [filterExt]);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#fff', padding: '0 20px' }}>
        <Title level={3} style={{ margin: 0 }}>File Manager</Title>
        <Button onClick={onLogout}>Logout</Button>
      </Header>
      <Content style={{ padding: '20px' }}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <UploadButton onUploadComplete={loadFiles} />
          <FileTable 
            files={files} 
            loading={loading} 
            onRefresh={loadFiles}
            filterExt={filterExt}
            setFilterExt={setFilterExt}
          />
        </Space>
      </Content>
    </Layout>
  );
}
