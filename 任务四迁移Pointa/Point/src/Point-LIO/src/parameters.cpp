#include "parameters.h"

bool is_first_frame = true;
double lidar_end_time = 0.0, first_lidar_time = 0.0, time_con = 0.0;
double last_timestamp_lidar = -1.0, last_timestamp_imu = -1.0;
int pcd_index = 0;
IVoxType::Options ivox_options_;
int ivox_nearby_type = 6;

std::vector<double> extrinT(3, 0.0);
std::vector<double> extrinR(9, 0.0);
state_input state_in;
state_output state_out;
std::string lid_topic, imu_topic;
bool prop_at_freq_of_imu = true, check_satu = true, con_frame = false, cut_frame = false;
bool use_imu_as_input = false, space_down_sample = true, publish_odometry_without_downsample = false;
int  init_map_size = 10, con_frame_num = 1;
double match_s = 81, satu_acc, satu_gyro, cut_frame_time_interval = 0.1;
float  plane_thr = 0.1f;
double filter_size_surf_min = 0.5, filter_size_map_min = 0.5, fov_deg = 180;
// double cube_len = 2000; 
float  DET_RANGE = 450;
bool   imu_en = true;
double imu_time_inte = 0.005;
double laser_point_cov = 0.01, acc_norm;
double vel_cov, acc_cov_input, gyr_cov_input;
double gyr_cov_output, acc_cov_output, b_gyr_cov, b_acc_cov;
double imu_meas_acc_cov, imu_meas_omg_cov; 
int    lidar_type, pcd_save_interval;
std::vector<double> gravity_init, gravity;
bool   runtime_pos_log, pcd_save_en, path_en, extrinsic_est_en = true;
bool   scan_pub_en, scan_body_pub_en;
shared_ptr<Preprocess> p_pre;
shared_ptr<ImuProcess> p_imu;
double time_update_last = 0.0, time_current = 0.0, time_predict_last_const = 0.0, t_last = 0.0;
double time_diff_lidar_to_imu = 0.0;

double lidar_time_inte = 0.1, first_imu_time = 0.0;
int cut_frame_num = 1, orig_odom_freq = 10;
double online_refine_time = 20.0; //unit: s
bool cut_frame_init = false; // true;

MeasureGroup Measures;

ofstream fout_out, fout_imu_pbp;

template <typename T>
static void declare_get(rclcpp::Node::SharedPtr &nh, const std::string &name, T &var, const T &def)
{
  nh->declare_parameter<T>(name, def);
  nh->get_parameter(name, var);
}

void readParameters(rclcpp::Node::SharedPtr &nh)
{
  p_pre.reset(new Preprocess());
  p_imu.reset(new ImuProcess());
  declare_get(nh, "prop_at_freq_of_imu", prop_at_freq_of_imu, true);
  declare_get(nh, "use_imu_as_input", use_imu_as_input, false);
  declare_get(nh, "check_satu", check_satu, true);
  declare_get(nh, "init_map_size", init_map_size, 100);
  declare_get(nh, "space_down_sample", space_down_sample, true);
  declare_get(nh, "mapping.satu_acc", satu_acc, 3.0);
  declare_get(nh, "mapping.satu_gyro", satu_gyro, 35.0);
  declare_get(nh, "mapping.acc_norm", acc_norm, 1.0);
  declare_get(nh, "mapping.plane_thr", plane_thr, 0.05f);
  declare_get(nh, "point_filter_num", p_pre->point_filter_num, 2);
  declare_get(nh, "common.lid_topic", lid_topic, std::string("/livox/lidar"));
  declare_get(nh, "common.imu_topic", imu_topic, std::string("/livox/imu"));
  declare_get(nh, "common.con_frame", con_frame, false);
  declare_get(nh, "common.con_frame_num", con_frame_num, 1);
  declare_get(nh, "common.cut_frame", cut_frame, false);
  declare_get(nh, "common.cut_frame_time_interval", cut_frame_time_interval, 0.1);
  declare_get(nh, "common.time_diff_lidar_to_imu", time_diff_lidar_to_imu, 0.0);
  declare_get(nh, "filter_size_surf", filter_size_surf_min, 0.5);
  declare_get(nh, "filter_size_map", filter_size_map_min, 0.5);
  declare_get(nh, "mapping.det_range", DET_RANGE, 300.f);
  declare_get(nh, "mapping.fov_degree", fov_deg, 180.0);
  declare_get(nh, "mapping.imu_en", imu_en, true);
  declare_get(nh, "mapping.extrinsic_est_en", extrinsic_est_en, true);
  declare_get(nh, "mapping.imu_time_inte", imu_time_inte, 0.005);
  declare_get(nh, "mapping.lidar_meas_cov", laser_point_cov, 0.1);
  declare_get(nh, "mapping.acc_cov_input", acc_cov_input, 0.1);
  declare_get(nh, "mapping.vel_cov", vel_cov, 20.0);
  declare_get(nh, "mapping.gyr_cov_input", gyr_cov_input, 0.1);
  declare_get(nh, "mapping.gyr_cov_output", gyr_cov_output, 0.1);
  declare_get(nh, "mapping.acc_cov_output", acc_cov_output, 0.1);
  declare_get(nh, "mapping.b_gyr_cov", b_gyr_cov, 0.0001);
  declare_get(nh, "mapping.b_acc_cov", b_acc_cov, 0.0001);
  declare_get(nh, "mapping.imu_meas_acc_cov", imu_meas_acc_cov, 0.1);
  declare_get(nh, "mapping.imu_meas_omg_cov", imu_meas_omg_cov, 0.1);
  declare_get(nh, "preprocess.blind", p_pre->blind, 1.0);
  declare_get(nh, "preprocess.lidar_type", lidar_type, 2);
  declare_get(nh, "preprocess.scan_line", p_pre->N_SCANS, 16);
  declare_get(nh, "preprocess.scan_rate", p_pre->SCAN_RATE, 10);
  declare_get(nh, "preprocess.timestamp_unit", p_pre->time_unit, 1);
  declare_get(nh, "mapping.match_s", match_s, 81.0);
  declare_get(nh, "mapping.gravity", gravity, std::vector<double>());
  declare_get(nh, "mapping.gravity_init", gravity_init, std::vector<double>());
  declare_get(nh, "mapping.extrinsic_T", extrinT, std::vector<double>());
  declare_get(nh, "mapping.extrinsic_R", extrinR, std::vector<double>());
  declare_get(nh, "odometry.publish_odometry_without_downsample", publish_odometry_without_downsample, false);
  declare_get(nh, "publish.path_en", path_en, true);
  declare_get(nh, "publish.scan_publish_en", scan_pub_en, true);
  declare_get(nh, "publish.scan_bodyframe_pub_en", scan_body_pub_en, true);
  declare_get(nh, "runtime_pos_log_enable", runtime_pos_log, false);
  declare_get(nh, "pcd_save.pcd_save_en", pcd_save_en, false);
  declare_get(nh, "pcd_save.interval", pcd_save_interval, -1);

  declare_get(nh, "mapping.lidar_time_inte", lidar_time_inte, 0.1);

  declare_get(nh, "mapping.ivox_grid_resolution", ivox_options_.resolution_, 0.2f);
  declare_get(nh, "ivox_nearby_type", ivox_nearby_type, 18);
  if (ivox_nearby_type == 0) {
    ivox_options_.nearby_type_ = IVoxType::NearbyType::CENTER;
  } else if (ivox_nearby_type == 6) {
    ivox_options_.nearby_type_ = IVoxType::NearbyType::NEARBY6;
  } else if (ivox_nearby_type == 18) {
    ivox_options_.nearby_type_ = IVoxType::NearbyType::NEARBY18;
  } else if (ivox_nearby_type == 26) {
    ivox_options_.nearby_type_ = IVoxType::NearbyType::NEARBY26;
  } else {
    ivox_options_.nearby_type_ = IVoxType::NearbyType::NEARBY18;
  }
    p_imu->gravity_ << VEC_FROM_ARRAY(gravity);
}

Eigen::Matrix<double, 3, 1> SO3ToEuler(const SO3 &rot) 
{
    double sy = sqrt(rot(0,0)*rot(0,0) + rot(1,0)*rot(1,0));
    bool singular = sy < 1e-6;
    double x, y, z;
    if(!singular)
    {
        x = atan2(rot(2, 1), rot(2, 2));
        y = atan2(-rot(2, 0), sy);   
        z = atan2(rot(1, 0), rot(0, 0));  
    }
    else
    {    
        x = atan2(-rot(1, 2), rot(1, 1));    
        y = atan2(-rot(2, 0), sy);    
        z = 0;
    }
    Eigen::Matrix<double, 3, 1> ang(x, y, z);
    return ang;
}

void open_file()
{

    fout_out.open(DEBUG_FILE_DIR("mat_out.txt"),ios::out);
    fout_imu_pbp.open(DEBUG_FILE_DIR("imu_pbp.txt"),ios::out);
    if (fout_out && fout_imu_pbp)
        cout << "~~~~"<<ROOT_DIR<<" file opened" << endl;
    else
        cout << "~~~~"<<ROOT_DIR<<" doesn't exist" << endl;

}

void reset_cov(Eigen::Matrix<double, 24, 24> & P_init)
{
    P_init = MD(24, 24)::Identity() * 0.1;
    P_init.block<3, 3>(21, 21) = MD(3,3)::Identity() * 0.0001;
    P_init.block<6, 6>(15, 15) = MD(6,6)::Identity() * 0.001;
}

void reset_cov_output(Eigen::Matrix<double, 30, 30> & P_init_output)
{
    P_init_output = MD(30, 30)::Identity() * 0.01;
    P_init_output.block<3, 3>(21, 21) = MD(3,3)::Identity() * 0.0001;
    // P_init_output.block<6, 6>(6, 6) = MD(6,6)::Identity() * 0.0001;
    P_init_output.block<6, 6>(24, 24) = MD(6,6)::Identity() * 0.001;
}