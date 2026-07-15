import axiosClient from './axiosClient';

const authApi = {
  register: (data) => {
    return axiosClient.post('/auth/register', data);
  },
  login: (data) => {
    // Nếu API login của bạn nhận JSON, dùng dòng dưới:
    return axiosClient.post('/auth/login', data);
    
    // MẸO: Nếu Backend dùng OAuth2PasswordRequestForm của FastAPI (truyền x-www-form-urlencoded), hãy đổi thành:
    // const formData = new URLSearchParams();
    // formData.append('username', data.email); // Hoặc data.username tùy backend
    // formData.append('password', data.password);
    // return axiosClient.post('/auth/login', formData, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
  },
  getMe: () => {
    return axiosClient.get('/users/me');
  }
};

export default authApi;