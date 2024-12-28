// Setup path configuration for shared services
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export function setupSharedPath() {
    // Add shared directory to module paths
    const sharedRoot = path.resolve(__dirname, '..');
    
    if (!process.env.NODE_PATH) {
        process.env.NODE_PATH = '';
    }
    
    if (!process.env.NODE_PATH.includes(sharedRoot)) {
        process.env.NODE_PATH = `${sharedRoot}:${process.env.NODE_PATH}`;
    }
    
    // Force module loader to reload cache
    require('module').Module._initPaths();
}

export default setupSharedPath;
