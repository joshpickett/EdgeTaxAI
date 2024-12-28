import { setupSharedPath } from './setup_path';
setupSharedPath();

import { apiClient } from './apiClient';
import config from 'config';
import { handleApiError } from 'utils/errorHandler';

class AIService {
    constructor() {
...rest of the code...
