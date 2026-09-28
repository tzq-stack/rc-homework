#pragma once
#include <common_lib.h>
#include "Estimator.h"
#include <sensor_msgs/msg/point_cloud2.hpp>

// 最大缓存数组长度，72万，用于存储绘图/时序记录数组T1、s_plot等
#define MAXN                (720000)

// ========== 全局外部变量声明（在cpp中定义，别处extern引用） ==========
// 数据累积、在线标定状态标志位
extern bool data_accum_finished, data_accum_start, online_calib_finish, refine_print;
extern int frame_num_init;

// 时间差、时间戳相关
extern double time_lag_IMU_wtr_lidar, move_start_time, online_calib_starts_time; 
extern double timediff_imu_wrt_lidar;    // IMU相对lidar的时间偏移量(时间标定结果)
extern bool timediff_set_flg;           // 时间偏移是否求解完成标志

extern V3D gravity_lio;                 // LIO估计出的重力向量

// 线程同步：互斥锁 + 条件变量，保护雷达IMU缓存队列
extern mutex mtx_buffer;
extern condition_variable sig_buffer;

extern int scan_count;
extern int frame_ct, wait_num;

// 雷达点云缓存队列：点云智能指针 + 对应时间戳队列
extern std::deque<PointCloudXYZI::Ptr>  lidar_buffer;
extern std::deque<double>               time_buffer;

// IMU数据双端队列缓存
extern std::deque<sensor_msgs::msg::Imu::SharedPtr> imu_deque;
extern std::mutex m_time;

// 消息是否已经推入缓存的标记
extern bool lidar_pushed, imu_pushed;
extern double imu_first_time;
extern bool lose_lid;                    // 是否丢失雷达数据标志

// 保存插值用前后两帧IMU
extern sensor_msgs::msg::Imu imu_last, imu_next;

extern PointCloudXYZI::Ptr  ptr_con;

// 用于rosbag回放/绘图保存大数组，MAXN=720000容量
extern double T1[MAXN], s_plot[MAXN], s_plot2[MAXN], s_plot3[MAXN], s_plot11[MAXN];

// ========== 回调函数声明 ==========
/**
 * @brief 普通标准PointCloud2点云回调，适用于Velodyne、Ouster等通用雷达
 */
void standard_pcl_cbk(const sensor_msgs::msg::PointCloud2::ConstSharedPtr &msg);

/**
 * @brief IMU话题回调函数，接收IMU原始测量，推入imu_deque队列
 */
void imu_cbk(const sensor_msgs::msg::Imu::ConstSharedPtr &msg_in);

/**
 * @brief 核心同步函数：从lidar_buffer、imu_deque提取时间对齐的一组测量，输出MeasureGroup
 *        逻辑：取一帧雷达，在时间区间内截取对应IMU序列，完成IMU插值封装给Estimator求解
 * @param meas 输出，一组对齐好的lidar+imu测量数据
 * @return true成功取出一组同步数据；false：数据不足，等待新消息
 */
bool sync_packages(MeasureGroup &meas);

