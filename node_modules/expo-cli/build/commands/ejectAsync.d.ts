import { EjectAsyncOptions } from './eject/prebuildAsync';
export declare function actionAsync(projectRoot: string, { platform, ...options }: Omit<EjectAsyncOptions, 'platforms'> & {
    npm?: boolean;
    platform?: string;
}): Promise<void>;
