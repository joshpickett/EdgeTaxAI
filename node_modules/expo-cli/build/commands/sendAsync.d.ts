import { URLOptions } from '../urlOpts';
declare type Options = Partial<URLOptions & {
    sendTo?: string;
}>;
export declare function actionAsync(projectRoot: string, options: Options): Promise<void>;
export {};
