import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Member {
  member_id: number;
  first_name: string;
  last_name: string;
  email: string;
  date_of_birth: string;
  gender: string;
  registration_date: string;
}

export interface Trainer {
  trainer_id: number;
  first_name: string;
  last_name: string;
  email: string;
  specialization: string;
  hire_date: string;
}

export interface Room {
  room_id: number;
  room_name: string;
  capacity: number;
  room_type: string;
}

export interface GroupClass {
  class_id: number;
  class_name: string;
  trainer_id: number;
  room_id: number;
  scheduled_date: string;
  start_time: string;
  end_time: string;
  capacity: number;
  current_enrollment?: number;
  is_full?: boolean;
}

export interface PTSession {
  session_id: number;
  member_id: number;
  trainer_id: number;
  room_id: number;
  scheduled_date: string;
  start_time: string;
  end_time: string;
  status: string;
  notes?: string;
}

export interface ClassEnrollment {
  enrollment_id: number;
  member_id: number;
  class_id: number;
  enrollment_date: string;
  attendance_status: string;
}

// Member API
export const memberAPI = {
  register: async (data: {
    first_name: string;
    last_name: string;
    email: string;
    date_of_birth: string;
    gender: string;
  }): Promise<Member> => {
    const response = await api.post('/members/', data);
    return response.data;
  },

  getDashboard: async (memberId: number) => {
    const response = await api.get(`/members/${memberId}/dashboard`);
    return response.data;
  },

  bookPTSession: async (data: {
    member_id: number;
    trainer_id: number;
    room_id: number;
    scheduled_date: string;
    start_time: string;
    end_time: string;
    notes?: string;
  }): Promise<PTSession> => {
    const response = await api.post('/sessions/pt', data);
    return response.data;
  },

  enrollInClass: async (memberId: number, classId: number): Promise<ClassEnrollment> => {
    const response = await api.post('/classes/enroll', {
      member_id: memberId,
      class_id: classId,
    });
    return response.data;
  },
};

// Trainer API
export const trainerAPI = {
  getSchedule: async (trainerId: number, startDate: string, endDate: string) => {
    const response = await api.post('/trainers/schedule', {
      trainer_id: trainerId,
      start_date: startDate,
      end_date: endDate,
    });
    return response.data;
  },

  searchMembers: async (trainerId: number, query: string): Promise<Member[]> => {
    const response = await api.get(`/trainers/${trainerId}/members/search?query=${query}`);
    return response.data;
  },

  getMemberProfile: async (memberId: number) => {
    const response = await api.get(`/trainers/members/${memberId}`);
    return response.data;
  },

  updateSessionStatus: async (sessionId: number, status: string) => {
    const response = await api.put('/trainers/sessions/status', {
      session_id: sessionId,
      status,
    });
    return response.data;
  },

  updateSessionNotes: async (sessionId: number, notes: string) => {
    const response = await api.put('/trainers/sessions/notes', {
      session_id: sessionId,
      notes,
    });
    return response.data;
  },
};

// Admin API
export const adminAPI = {
  getMembers: async (): Promise<Member[]> => {
    const response = await api.get('/admin/members');
    return response.data;
  },

  getTrainers: async (): Promise<Trainer[]> => {
    const response = await api.get('/admin/trainers');
    return response.data;
  },

  getRooms: async (): Promise<Room[]> => {
    const response = await api.get('/admin/rooms');
    return response.data;
  },

  getClasses: async (): Promise<GroupClass[]> => {
    const response = await api.get('/admin/classes');
    return response.data;
  },

  addRoom: async (data: { name: string; capacity: number; room_type?: string }): Promise<Room> => {
    const response = await api.post('/admin/rooms', data);
    return response.data;
  },

  addTrainer: async (data: {
    first_name: string;
    last_name: string;
    email: string;
    specialization: string;
  }): Promise<Trainer> => {
    const response = await api.post('/admin/trainers', data);
    return response.data;
  },

  createClass: async (data: {
    name: string;
    trainer_id: number;
    room_id: number;
    scheduled_date: string;
    start_time: string;
    end_time: string;
    capacity: number;
  }): Promise<GroupClass> => {
    const response = await api.post('/admin/classes', data);
    return response.data;
  },

  rescheduleClass: async (classId: number, newDate: string, newStart: string, newEnd: string) => {
    const response = await api.put('/admin/classes/reschedule', {
      class_id: classId,
      new_date: newDate,
      new_start: newStart,
      new_end: newEnd,
    });
    return response.data;
  },

  cancelClass: async (classId: number) => {
    const response = await api.delete(`/admin/classes/${classId}`);
    return response.data;
  },
};

// Common API
export const commonAPI = {
  getMembers: async (): Promise<Member[]> => {
    const response = await api.get('/members/');
    return response.data;
  },

  getTrainers: async (): Promise<Trainer[]> => {
    const response = await api.get('/trainers/');
    return response.data;
  },

  getRooms: async (): Promise<Room[]> => {
    const response = await api.get('/rooms/');
    return response.data;
  },

  getClasses: async (): Promise<GroupClass[]> => {
    const response = await api.get('/classes/');
    return response.data;
  },
};

export default api;

